# 🛒 Instacart Market Basket Analysis Dashboard

An interactive data analysis dashboard built on the real [Instacart Market Basket dataset](https://www.kaggle.com/datasets/yasserh/instacart-online-grocery-basket-analysis-dataset) from Kaggle.

**Stack:** Python · SQLite · Streamlit · Plotly

---

## 📊 Dashboard Features

- **KPI Overview** — total orders, unique users, items ordered, avg basket size, reorder rate
- **Shopping Patterns** — orders by hour of day and day of week
- **Top Products** — most ordered and most reordered products, colored by reorder rate
- **Department & Aisle Breakdown** — filterable donut chart and bar charts
- **User Behaviour** — days-between-orders distribution and order frequency per user
- **Cart Position Analysis** — dual-axis chart of basket position vs reorder rate
- **Live SQL Explorer** — write and run any SELECT query with auto-charting

---

## 🗃️ Database Stats

| Table | Rows |
|---|---|
| `orders` | 1,244,968 |
| `order_products` | 12,374,749 |
| `products` | 49,688 |
| `aisles` | 134 |
| `departments` | 21 |

*75,000 users sampled from the full 206K-user dataset for performance.*

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/instacart-dashboard.git
cd instacart-dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the dataset

Download from Kaggle: [Instacart Online Grocery Basket Analysis](https://www.kaggle.com/datasets/yasserh/instacart-online-grocery-basket-analysis-dataset)

Place all CSV files into a `data/` folder inside the project directory:

```
instacart-dashboard/
├── data/
│   ├── orders.csv
│   ├── order_products__prior.csv
│   ├── order_products__train.csv
│   ├── products.csv
│   ├── aisles.csv
│   └── departments.csv
├── dashboard.py
├── setup_instacart_db.py
└── requirements.txt
```

### 4. Build the database

```bash
python setup_instacart_db.py
```

This samples 75,000 users and loads ~12.3M order-product rows into a local `instacart.db` SQLite database. Takes ~5–10 minutes.

### 5. Launch the dashboard

```bash
streamlit run dashboard.py
```

Open your browser at `http://localhost:8501`

---

## 🧠 SQL Highlights

Key queries demonstrated in this project:

- Multi-table JOINs across 5 relational tables
- Aggregations with `COUNT`, `SUM`, `AVG`, `ROUND`
- Parameterized filtering by department
- Reorder rate calculation using conditional aggregation
- Date/time analysis using `order_hour_of_day` and `order_dow`
- User-level behavioural metrics

---

## 📁 File Overview

| File | Description |
|---|---|
| `dashboard.py` | Streamlit dashboard app |
| `setup_instacart_db.py` | Builds the SQLite DB from raw CSVs |
| `requirements.txt` | Python dependencies |

---

## 📌 Data Source

Instacart Online Grocery Shopping Dataset 2017, via [Kaggle](https://www.kaggle.com/datasets/yasserh/instacart-online-grocery-basket-analysis-dataset).
