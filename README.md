# Instacart Market Basket Analysis

Interactive dashboard for exploring the Instacart grocery ordering dataset. Built this to practice working with large relational datasets and get more comfortable with SQL aggregations and Streamlit.

**Stack:** Python, SQLite, Streamlit, Plotly

---

## What it does

The dashboard lets you filter by department and explore:

- Order volume by hour of day and day of week
- Most ordered and most reordered products
- Department and aisle breakdown
- How many orders users typically place, and how often they come back
- Whether items added earlier in the cart get reordered more
- A SQL explorer where you can run your own queries against the database

---

## Setup

Download the dataset from [Kaggle](https://www.kaggle.com/datasets/yasserh/instacart-online-grocery-basket-analysis-dataset) and put the CSVs in a `data/` folder.

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

Install dependencies:

```bash
pip install -r requirements.txt
```

Build the database (samples 75K users from the full dataset, takes ~5–10 min):

```bash
python setup_instacart_db.py
```

Run the dashboard:

```bash
streamlit run dashboard.py
```

---

## Dataset

The full dataset has 3.4M orders and 32M+ order-product rows across 206K users. I sampled 75K users to keep the database to a manageable size (~800MB) while still having 12.3M rows to query against.

Source: [Instacart Online Grocery Shopping Dataset 2017](https://www.kaggle.com/datasets/yasserh/instacart-online-grocery-basket-analysis-dataset)
