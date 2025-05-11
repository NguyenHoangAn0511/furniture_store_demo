import json
import sqlite3
import os

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "store.db")

# Load JSON files
with open(os.path.join(DATA_DIR, "customers.json")) as f:
    customers = json.load(f)

with open(os.path.join(DATA_DIR, "products.json")) as f:
    products = json.load(f)

with open(os.path.join(DATA_DIR, "orders.json")) as f:
    orders = json.load(f)

with open(os.path.join(DATA_DIR, "mappings.json")) as f:
    mappings = json.load(f)

# Create DB
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Drop old tables
c.executescript("""
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    location TEXT
);

CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    name TEXT,
    category INTEGER,
    price REAL,
    description TEXT,
    stock INTEGER,
    length_cm INTEGER,
    material INTEGER,
    color INTEGER,
    includes_pillow INTEGER,
    has_table_option INTEGER,
    table_discount_info TEXT,
    warranty_info INTEGER,
    care_instructions INTEGER,
    weight_limit_kg INTEGER,
    pet_friendly INTEGER
);

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_date TEXT,
    delivery_date TEXT,
    status INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    product_id TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
""")

# Insert customers
for c_data in customers:
    c.execute("""
        INSERT INTO customers (customer_id, name, email, phone, location)
        VALUES (?, ?, ?, ?, ?)
    """, (
        c_data["customer_id"],
        c_data["name"],
        c_data["email"],
        c_data["phone"],
        c_data["location"]
    ))

# Insert products
for p in products:
    c.execute("""
        INSERT INTO products (
            product_id, name, category, price, description, stock,
            length_cm, material, color, includes_pillow,
            has_table_option, table_discount_info, warranty_info,
            care_instructions, weight_limit_kg, pet_friendly
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p["product_id"],
        p["name"],
        mappings["category"].get(p["category"], -1),
        p["price"],
        p["description"],
        p["stock"],
        p["length_cm"],
        mappings["material"].get(p["material"], -1),
        mappings["color"].get(p["color"], -1),
        p["includes_pillow"],
        p["has_table_option"],
        p["table_discount_info"],
        mappings["warranty_info"].get(p["warranty_info"], -1),
        mappings["care_instructions"].get(p["care_instructions"], -1),
        p["weight_limit_kg"],
        p["pet_friendly"]
    ))

# Insert orders + order_items
for o in orders:
    c.execute("""
        INSERT INTO orders (order_id, customer_id, order_date, delivery_date, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        o["order_id"],
        o["customer_id"],
        o["order_date"],
        o["delivery_date"],
        int(o["status"])
    ))
    for product_id in o["product_ids"]:
        c.execute("""
            INSERT INTO order_items (order_id, product_id)
            VALUES (?, ?)
        """, (o["order_id"], product_id))

conn.commit()
conn.close()

print("✅ store.db created with structured and mapped data.")
