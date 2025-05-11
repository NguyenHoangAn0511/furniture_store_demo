import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyCVa2BWlFYEBPe6VkfYZIRD0MWNnHkIJIU")

model = genai.GenerativeModel("gemini-2.0-flash")


def detect_intent_llm(user_input):
    prompt = f"""
    Classify the user's intent from the following input:
    "{user_input}"

    Possible intents:
    - greeting
    - farewell
    - gratitude
    - sql_query
    - insult

    Respond with the intent label only.
    """
    response = model.generate_content(prompt) # Replace with your LLM API call
    return response.text.strip().lower()



def generate_sql_from_question(question, schema):
    status_mapping = """
        # in the 'orders' table, the 'status' field uses numeric codes:
        # 0 = 'pending'
        # 1 = 'shipped'
        # 2 = 'delivered'
        # when selecting the status, use a case expression like:
        #   case status
        #     when 0 then 'pending'
        #     when 1 then 'shipped'
        #     when 2 then 'delivered'
        #   end as status
        """

    prompt = f"""
You are a helpful assistant, you provide help to customer of a furniture store in Australia. Your task is to convert this natural language question into an SQL query (SQLite) based on the database schema below:

### Status Mapping:
- In the 'orders' table, the 'status' field uses numeric codes:
  - 0 = 'pending'
  - 1 = 'shipped'
  - 2 = 'delivered'
- When selecting the status, use a case expression like:
  ```sql
  case status
    when 0 then 'pending'
    when 1 then 'shipped'
    when 2 then 'delivered'
  end as status
Database Schema:
{schema}

Product Data Mappings:
Here are the mappings for product attributes to integers for easier integration with LLM:

category:
'sofa': 0
'table': 1
'chair': 2
'bed': 3
'storage': 4
'desk': 5
material:
'soft velvet': 0
'leather': 1
'eco-leather': 2
'pet-friendly fabric': 3
'cotton blend': 4
'linen': 5
'microfiber': 6
'recycled polyester': 7

color:
'beige': 0
'gray': 1
'blue': 2
'green': 3
'brown': 4
'white': 5
'black': 6

warranty_info:
'1-year warranty': 0
'2-year warranty': 1
'3-year warranty': 2
'5-year warranty': 3

care_instructions:
'wipe with damp cloth': 0
'use fabric cleaner': 1
'vacuum regularly': 2
'machine-washable covers': 3
'leather conditioner monthly': 4

includes_pillow: 1 for Yes, 0 for No
has_table_option: 1 for Yes, 0 for No
pet_friendly: 1 for Yes, 0 for No
weight_limit_kg: Direct integer value (e.g., 200, 250, 300)

### Guidelines for generating the SQL query:
- If the question is not clear, ask for clarification.
- If the question is too complex, break it down into simpler parts.
- Think step by step and explain your reasoning.
- If the question is not related to the database, say what you can do.
- Use select * to get all fields from the table if needed.
- Use select with specific fields to get only the required fields.
- Use query that is compatible with SQLite.
- Use query that join tables to return products, customers, and orders name instead of ID.
- Use the correct table names and field names as per the schema.
- Use the correct data types for each field.
- Use the query that is efficient and optimized for performance.
- Use the query that return item name instead of ID.
- Use limit when to limit the number of records returned, 10 is enough.
- Use order by when necessary to sort the results.
- Write the SQL query in all lowercase.
- Use single quotes (' ') for string literals, never double quotes.
- Do not use backticks or any markdown formatting like triple backticks.
- Use `like '%text%'` for filtering by customer name or product name to allow for partial matches.
- When working with product-related queries, **always prioritize filtering by category first**. If no category matches, then filter by product name.
- For order statuses, **use a case expression** to convert numeric order statuses into human-readable values:
    - 0 = 'pending'
    - 1 = 'shipped'
    - 2 = 'delivered'
- If customer ask about order, only return order information if the customer name or id or order id is provided.
- Only return the SQL query, no explanation, no text formatting like 'sql', 'python', etc.
- Order ID should be in the format of 'Oxxxx'.
### Question:
    {question}
    SQL Query (only return the SQL query, no explanation, no text formatting like 'sql', 'python', etc.):
"""
    response = model.generate_content(prompt)
    return response.text.strip("` \n").replace("sql", "").replace("python", "").replace("ite", "")

def rephrase_answer(question, sql, result):
    prompt = f"""
        You are a helpful assistant that working in a furniture store in Australia.
        You will provide helpful and concise answers to customer questions based on the results from a database query.
        You need to rephrase the answer to make it more natural and human-like.
        Be friendly and polite in your response.
        Product Data Mappings:
            Here are the mappings for product attributes to integers for easier integration with LLM:
            category:
            'sofa': 0
            'table': 1
            'chair': 2
            'bed': 3
            'storage': 4
            'desk': 5
            material:
            'soft velvet': 0
            'leather': 1
            'eco-leather': 2
            'pet-friendly fabric': 3
            'cotton blend': 4
            'linen': 5
            'microfiber': 6
            'recycled polyester': 7

            color:
            'beige': 0
            'gray': 1
            'blue': 2
            'green': 3
            'brown': 4
            'white': 5
            'black': 6

            warranty_info:
            '1-year warranty': 0
            '2-year warranty': 1
            '3-year warranty': 2
            '5-year warranty': 3

            care_instructions:
            'wipe with damp cloth': 0
            'use fabric cleaner': 1
            'vacuum regularly': 2
            'machine-washable covers': 3
            'leather conditioner monthly': 4

            includes_pillow: 1 for Yes, 0 for No
            has_table_option: 1 for Yes, 0 for No
            pet_friendly: 1 for Yes, 0 for No
            weight_limit_kg: Direct integer value (e.g., 200, 250, 300)

            In the 'orders' table, the 'status' field uses numeric codes:
            # 0 = 'pending'
            # 1 = 'shipped'
            # 2 = 'delivered'
        Given the question:
        {question}

        This is the SQL query that was generated:
        {sql}

        And the result from the database:
        {result}

        If the result is empty, say "Sorry, I couldn't find any information related to your question."
        If the result is not empty, summarize the results and provide a clear answer.
        If the result contains multiple records, markdown is prefered.

        Write a clear, concise natural language answer to the question:
        """
    response = model.generate_content(prompt)
    return response.text.strip()
