import streamlit as st
from llm_utils import detect_intent_llm, generate_sql_from_question, rephrase_answer
from query_helper import get_db_schema, execute_sql
import json
import sqlite3

DB_PATH = "data/store.db"

st.set_page_config(page_title="🧠 Gemini RAG-SQL Assistant", layout="wide")
st.title("🔎 Gemini RAG-SQL Assistant for Store DB")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Ask me anything about your store database."}]
if "schema" not in st.session_state:
    st.session_state.schema = get_db_schema(DB_PATH)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Build chat history string for LLM prompt
def build_conversation_prompt(current_question):
    history_text = ""
    for msg in st.session_state.messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"
    history_text += f"User: {current_question}\nAssistant:"
    return history_text

# User input
if prompt := st.chat_input("Ask a question about customers, orders, or products:"):
    # Display user input
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Combine full chat history into the prompt
    conversation_prompt = build_conversation_prompt(prompt)
    print(conversation_prompt)

    

    with st.spinner("🔧 Generating SQL with Gemini..."):
        try:
            # Use conversation history in prompt to generate SQL
            intent = detect_intent_llm(prompt)
            print(intent)
            if intent != "sql_query":
                responses = {
                    "greeting": "Hello! How can I assist you today?",
                    "farewell": "Goodbye! Have a great day!",
                    "gratitude": "You're welcome!",
                    "smalltalk": "I'm here to help you with your database queries.",
                }
                st.chat_message("assistant").markdown(responses.get(intent, "I'm here to assist you."))
            else:
                sql = generate_sql_from_question(conversation_prompt, st.session_state.schema)
                st.code(sql, language="sql")

                # Execute SQL query
                try:
                    result = execute_sql(DB_PATH, sql)
                    if len(result) == 0:
                        result.append({"error": "No results found."})
                    # if "error" in result[0]:
                    #     st.error(f"❌ Error: {result[0]['error']}")
                    # else:
                    # Rephrase the result naturally
                    with st.spinner("🧠 Rephrasing result..."):
                        plain_answer = rephrase_answer(prompt, sql, json.dumps(result))
                        st.chat_message("assistant").markdown(plain_answer)
                        st.session_state.messages.append({"role": "assistant", "content": plain_answer})
                except Exception as e:
                    st.error(f"❌ Query Execution Error: {str(e)}")

        except Exception as e:
            st.error(f"❌ SQL Generation Error: {str(e)}")
