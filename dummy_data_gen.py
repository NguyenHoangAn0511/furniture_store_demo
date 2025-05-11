import json
import random
from faker import Faker
from datetime import timedelta
from collections import defaultdict
import os

fake = Faker()

NUM_CUSTOMERS = 200
NUM_PRODUCTS = 1000
NUM_ORDERS = 20000
SOFA_RATIO = 0.3

CATEGORY_MAP = {
    0: "sofa",
    1: "table",
    2: "chair",
    3: "bed",
    4: "storage",
    5: "desk"
}

MATERIAL_MAP = {
    0: "soft velvet",
    1: "leather",
    2: "eco-leather",
    3: "pet-friendly fabric",
    4: "cotton blend",
    5: "linen",
    6: "microfiber",
    7: "recycled polyester"
}

COLOR_MAP = {
    0: "beige",
    1: "gray",
    2: "blue",
    3: "green",
    4: "brown",
    5: "white",
    6: "black"
}

WARRANTY_MAP = {
    0: "1-year warranty",
    1: "2-year warranty",
    2: "3-year warranty",
    3: "5-year warranty"
}

CARE_INSTRUCTIONS_MAP = {
    0: "Wipe with damp cloth",
    1: "Use fabric cleaner",
    2: "Vacuum regularly",
    3: "Machine-washable covers",
    4: "Leather conditioner monthly"
}


def generate_customers(n):
    return [
        {
            "customer_id": f"C{1000+i}",
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "location": fake.city()
        }
        for i in range(n)
    ]

def generate_products(n, sofa_ratio=0.3):
    products = []
    num_sofas = int(n * sofa_ratio)
    categories = list(CATEGORY_MAP.keys())
    materials = list(MATERIAL_MAP.keys())
    colors = list(COLOR_MAP.keys())
    warranties = list(WARRANTY_MAP.keys())
    care_instructions = list(CARE_INSTRUCTIONS_MAP.keys())
    table_discount_samples = [
        "10% off when bought with matching table",
        "Free shipping when purchased with coffee table",
        "Bundle offer: sofa + table at $999",
        "No discount for table combo"
    ]

    for i in range(n):
        is_sofa = i < num_sofas
        category = 0 if is_sofa else random.choice(categories[1:])

        product = {
            "product_id": f"P{1000+i}",
            "name": f"{fake.word().capitalize()} {CATEGORY_MAP[category]}",
            "category": CATEGORY_MAP[category],
            "price": round(random.uniform(100, 2000), 2),
            "description": fake.sentence(),
            "stock": random.randint(2000, 3000),
            "length_cm": random.choice([180, 190, 200, 210, 220]),
            "material": MATERIAL_MAP[random.choice(materials)],
            "color": COLOR_MAP[random.choice(colors)],
            "includes_pillow": int(random.random() < 0.5),
            "has_table_option": int(random.random() < 0.5),
            "table_discount_info": random.choice(table_discount_samples),
            "warranty_info": WARRANTY_MAP[random.choice(warranties)],
            "care_instructions": CARE_INSTRUCTIONS_MAP[random.choice(care_instructions)],
            "weight_limit_kg": random.choice([200, 250, 300]),
            "pet_friendly": int(random.random() < 0.6)
        }
        products.append(product)

    return products

def generate_orders(num_orders, customers, products):
    orders = []
    product_stock = {p["product_id"]: p["stock"] for p in products}
    used_products = defaultdict(int)

    for i in range(num_orders):
        customer = random.choice(customers)
        num_items = random.randint(1, 3)
        available_products = [p for p in products if product_stock[p["product_id"]] > 0]
        if not available_products:
            break
        selected = random.sample(available_products, min(num_items, len(available_products)))

        product_ids = []
        for product in selected:
            pid = product["product_id"]
            if product_stock[pid] > 0:
                product_ids.append(pid)
                product_stock[pid] -= 1
                used_products[pid] += 1

        if not product_ids:
            continue

        order_date = fake.date_between(start_date='-6M', end_date='today')
        delivery_date = order_date + timedelta(days=random.randint(2, 7))
        status = random.choice(["0", "1", "2"])

        orders.append({
            "order_id": f"O{1000+i}",
            "customer_id": customer["customer_id"],
            "product_ids": product_ids,
            "order_date": order_date.isoformat(),
            "delivery_date": delivery_date.isoformat(),
            "status": status
        })

    for p in products:
        pid = p["product_id"]
        p["stock"] = max(0, p["stock"] - used_products[pid])

    return orders, products

def save_to_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    customers = generate_customers(NUM_CUSTOMERS)
    products = generate_products(NUM_PRODUCTS, sofa_ratio=SOFA_RATIO)
    orders, updated_products = generate_orders(NUM_ORDERS, customers, products)

    save_to_json(customers, "data/customers.json")
    save_to_json(updated_products, "data/products.json")
    save_to_json(orders, "data/orders.json")

    mappings = {
        "category": {v: k for k, v in CATEGORY_MAP.items()},
        "material": {v: k for k, v in MATERIAL_MAP.items()},
        "color": {v: k for k, v in COLOR_MAP.items()},
        "warranty_info": {v: k for k, v in WARRANTY_MAP.items()},
        "care_instructions": {v: k for k, v in CARE_INSTRUCTIONS_MAP.items()}
    }
    save_to_json(mappings, "data/mappings.json")

    print("data/*.json files are generated.")
