"""
Instacart Market Basket — SQLite Database Builder
Samples 75,000 users (keeping all their orders & products) for a fast,
consistent, and impressive portfolio database (~8–12M order-product rows).
"""

import sqlite3
import pandas as pd
import numpy as np
import os, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH  = os.path.join(os.path.dirname(__file__), "instacart.db")

# ── 1. Load reference tables (small, load fully) ──────────────────────────────
print("Loading reference tables...")
aisles      = pd.read_csv(os.path.join(DATA_DIR, "aisles.csv"))
departments = pd.read_csv(os.path.join(DATA_DIR, "departments.csv"))
products    = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
print(f"  aisles: {len(aisles):,}  |  departments: {len(departments):,}  |  products: {len(products):,}")

# ── 2. Load orders & sample 75K users ─────────────────────────────────────────
print("Loading orders...")
orders_full = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
print(f"  Total orders: {len(orders_full):,}  |  Unique users: {orders_full['user_id'].nunique():,}")

N_USERS = 75_000
np.random.seed(42)
all_users   = orders_full["user_id"].unique()
sampled_users = np.random.choice(all_users, size=min(N_USERS, len(all_users)), replace=False)
sampled_set = set(sampled_users)

orders = orders_full[orders_full["user_id"].isin(sampled_set)].copy()
sampled_order_ids = set(orders["order_id"].tolist())
print(f"  Sampled orders: {len(orders):,}  ({len(sampled_users):,} users)")

# ── 3. Load order_products in chunks (prior = 32M rows) ───────────────────────
print("Loading order_products__prior (chunked, filtering to sampled orders)...")
prior_chunks = []
chunk_size   = 500_000
total_read   = 0

for chunk in pd.read_csv(
    os.path.join(DATA_DIR, "order_products__prior.csv"),
    chunksize=chunk_size
):
    filtered = chunk[chunk["order_id"].isin(sampled_order_ids)]
    prior_chunks.append(filtered)
    total_read += len(chunk)
    kept = sum(len(c) for c in prior_chunks)
    print(f"  read {total_read:,} rows  |  kept {kept:,}", end="\r")

order_products_prior = pd.concat(prior_chunks, ignore_index=True)
print(f"\n  Final prior rows: {len(order_products_prior):,}")

print("Loading order_products__train...")
train_all  = pd.read_csv(os.path.join(DATA_DIR, "order_products__train.csv"))
order_products_train = train_all[train_all["order_id"].isin(sampled_order_ids)].copy()
print(f"  Train rows kept: {len(order_products_train):,}")

# ── 4. Combine prior + train into one order_products table ────────────────────
order_products_prior["eval_set"] = "prior"
order_products_train["eval_set"] = "train"
order_products = pd.concat([order_products_prior, order_products_train], ignore_index=True)
print(f"  Total order_products: {len(order_products):,}")

# ── 5. Write to SQLite ─────────────────────────────────────────────────────────
print(f"\nWriting to {DB_PATH} ...")
conn = sqlite3.connect(DB_PATH)

print("  Writing aisles...")
aisles.to_sql("aisles", conn, if_exists="replace", index=False)

print("  Writing departments...")
departments.to_sql("departments", conn, if_exists="replace", index=False)

print("  Writing products...")
products.to_sql("products", conn, if_exists="replace", index=False)

print("  Writing orders...")
orders.to_sql("orders", conn, if_exists="replace", index=False, chunksize=50_000)

print("  Writing order_products (largest table, this takes a few minutes)...")
order_products.to_sql("order_products", conn, if_exists="replace", index=False,
                       chunksize=50_000)

# ── 6. Create indexes for dashboard query speed ────────────────────────────────
print("  Creating indexes...")
conn.execute("CREATE INDEX IF NOT EXISTS idx_op_order_id    ON order_products(order_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_op_product_id  ON order_products(product_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_op_reordered   ON order_products(reordered)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_user    ON orders(user_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_dow     ON orders(order_dow)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_hour    ON orders(order_hour_of_day)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_prod_dept      ON products(department_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_prod_aisle     ON products(aisle_id)")
conn.commit()

# ── 7. Summary ─────────────────────────────────────────────────────────────────
print("\n✅ instacart.db created!")
print(f"   aisles:         {conn.execute('SELECT COUNT(*) FROM aisles').fetchone()[0]:>10,}")
print(f"   departments:    {conn.execute('SELECT COUNT(*) FROM departments').fetchone()[0]:>10,}")
print(f"   products:       {conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]:>10,}")
print(f"   orders:         {conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]:>10,}")
print(f"   order_products: {conn.execute('SELECT COUNT(*) FROM order_products').fetchone()[0]:>10,}")
conn.close()
print(f"\nDB size: {os.path.getsize(DB_PATH) / 1e9:.2f} GB")
