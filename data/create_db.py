import sqlite3, random, datetime, os

random.seed(42)

os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/sales.db")
c = conn.cursor()

c.executescript("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT, category TEXT, cost_price REAL
);
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT, region TEXT, since_date TEXT
);
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    date TEXT, product TEXT, revenue REAL, units INTEGER,
    customer_id INTEGER, region TEXT
);
""")

products = [
    (1,"Starter Plan","SaaS",15.0),(2,"Growth Plan","SaaS",60.0),
    (3,"Enterprise Plan","SaaS",200.0),(4,"Onboarding Package","Services",80.0),
    (5,"Custom Integration","Services",300.0),
]
c.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?)", products)

regions = ["FR","DE","NL","BE","ES","IT"]
customers = [(i, f"Customer {i}", random.choice(regions),
              (datetime.date(2024,1,1)+datetime.timedelta(days=random.randint(0,365))).isoformat())
             for i in range(1, 101)]
c.executemany("INSERT OR IGNORE INTO customers VALUES (?,?,?,?)", customers)

sales = []
for i in range(1, 1001):
    d = datetime.date(2025, random.randint(1,12), random.randint(1,28))
    prod = random.choice(["Starter Plan","Growth Plan","Enterprise Plan","Onboarding Package","Custom Integration"])
    price_map = {"Starter Plan":49,"Growth Plan":199,"Enterprise Plan":900,"Onboarding Package":350,"Custom Integration":1200}
    units = random.randint(1,5)
    revenue = price_map[prod] * units * round(random.uniform(0.9,1.1), 2)
    cust_id = random.randint(1,100)
    region = customers[cust_id-1][2]
    sales.append((i, d.isoformat(), prod, round(revenue,2), units, cust_id, region))
c.executemany("INSERT OR IGNORE INTO sales VALUES (?,?,?,?,?,?,?)", sales)

conn.commit()
conn.close()
print("sales.db created with", len(sales), "rows")
