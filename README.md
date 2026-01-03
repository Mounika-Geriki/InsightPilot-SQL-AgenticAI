# 🚀 InsightPilot
### Agentic SQL Analytics Platform

InsightPilot is an end-to-end analytics project that demonstrates how to design and build a
**SQL-based data warehouse using a medallion architecture (Bronze, Silver, Gold)** and
layer **analytics dashboards and AI agents** on top to generate trusted business insights.

This project is built incrementally to reflect **real-world data engineering and analytics workflows**
used in big tech companies.

---

## 🎯 Problem Statement
Business and analytics teams often spend significant time manually:
- Querying raw data
- Validating KPIs
- Building dashboards
- Writing performance summaries

This process is slow, error-prone, and difficult to scale.

**InsightPilot** automates this workflow by combining:
- A structured SQL data warehouse
- Analytics-ready dashboards
- AI agents for validation, anomaly detection, and insight generation

---

## ✅ Current Progress (Day 1–3)

- ✔️ Defined business requirements, KPIs, and analytics use cases  
- ✔️ Designed a Medallion Architecture (Bronze / Silver / Gold)  
- ✔️ Initialized project repository and environment  
- ✔️ Ingested raw e-commerce data into DuckDB (Bronze layer)  
- ✔️ Preserved source schemas and validated record counts  

---

## 🏗️ Architecture (High Level)

---TBD


> AI agents operate **only on Gold-layer data** to ensure correctness and prevent hallucinations.

---

## 🛠️ Tech Stack

**Data & Storage**
- CSV (source data)
- DuckDB (analytical warehouse)

**Analytics**
- SQL (transformations & KPIs)
- Python (pandas, numpy)

**Dashboards**
- Streamlit
- Plotly

**AI / Agents (Upcoming)**
- Python-based agents
- LLM integration
- Rule-based validation

**Dev & Docs**
- GitHub
- Notion (project tracking)
- draw.io (architecture diagrams)

---

## 📂 Project Structure

```text
insightpilot/
├── data/
│   └── raw/                     # Raw source CSV files (Bronze input, not committed)
│
├── warehouse/
│   ├── init_db.py               # Bronze layer ingestion (CSV → DuckDB)
│   └── insightpilot.duckdb      # DuckDB warehouse (ignored in git)
│
├── sql/
│   ├── bronze/                  # (Optional) raw-level SQL references
│   ├── silver/                  # Cleaned & validated SQL views
│   └── gold/                    # Fact tables & KPI queries
│
├── agents/
│   ├── ingestion_agent.py       # (Upcoming) data ingestion agent
│   ├── dq_agent.py              # (Upcoming) data quality agent
│   ├── sql_agent.py             # (Upcoming) SQL analytics agent
│   └── insight_agent.py         # (Upcoming) insight explanation agent
│
├── app/
│   └── streamlit_app.py         # (Upcoming) Streamlit dashboards & AI interface
│
├── dashboards/
│   └── assets/                  # Dashboard screenshots / mockups
│
├── evaluation/
│   ├── test_questions.json      # Business questions for validation
│   └── checks.py                # Data & AI validation logic
│
├── .gitignore                   # Ignore data, venv, and local artifacts
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── .env.example                 # Environment variable template

```


---

## 📊 Dataset
This project uses the **Olist Brazilian E-commerce Dataset**, which includes:
- Orders
- Customers
- Products
- Sellers
- Payments
- Reviews
- Geolocation data

The dataset is well-suited for:
- Revenue analytics
- Funnel analysis
- Operational KPIs
- Anomaly detection


## 📌 Note
This project focuses on **data modeling, data quality, and analytics correctness first**.
The architecture is designed to be **portable to Spark, Airflow, and cloud warehouses**
in a production environment.

---

