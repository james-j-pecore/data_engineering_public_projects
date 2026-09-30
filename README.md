# Data Engineering & Analytics Portfolio

Welcome to my portfolio of data engineering, analytics, and applied machine learning projects.

These projects demonstrate how I approach real-world data problems: collecting and organizing data, designing reliable pipelines, building analytical models, and presenting results in a way that supports decision-making.

Across the portfolio, I focus on:

- **End-to-end data pipelines** using real and publicly available data
- **Applied machine learning and AI** with transparent, measurable evaluation
- **Analytics-ready data models** designed for reporting and downstream analysis
- **Cloud and data-platform architecture**
- **Clear, modular project structure** that reflects professional engineering practices
- **Documentation and diagnostics** that make systems easier to understand and maintain

---

## Project Scope

These projects are designed to demonstrate the engineering and analytical processes used in professional data environments.

They use public, personal, or simulated data and do not contain proprietary company models, confidential business logic, or investment strategies. Where financial modeling is involved, signal logic is intentionally simplified and is intended solely as a technical demonstration.

---

## Featured Projects

### [Spotify Analytics Pipeline](./spotify-dbt-analytics-pipeline)

An end-to-end analytics pipeline that transforms Spotify library and playlist data into structured datasets and interactive reporting.

**Key features:**
- Ingests live Spotify data, including playlist composition, artists, release years, and playlist overlap
- Uses **dbt** to clean, transform, and organize raw data into analytics-ready models
- Uses **Dagster** to coordinate pipeline workflows
- Presents results through an interactive **Streamlit dashboard**

**Business value:** Demonstrates how raw application data can be transformed into reliable datasets for behavioral and product analytics.

**Technologies:** Python, SQL, dbt, Dagster, Streamlit

<img src="spotify-dbt-analytics-pipeline/images/streamlit_overview.png" alt="Spotify Library Analytics dashboard overview" width="700">

---

### [AI-Enhanced Financial Analytics Pipeline](./ai-financial-signals-pipeline)

A financial data pipeline combining market data, statistical indicators, machine learning, and historical performance evaluation.

**Key features:**
- Ingests stock, cryptocurrency, and macroeconomic data
- Engineers commonly used market indicators including momentum, RSI, MACD, and moving averages
- Uses an **XGBoost classification model** to combine multiple indicators into a higher-level model output
- Includes historical backtesting and performance measurement
- Produces diagnostic visualizations for evaluating model behavior

**Business value:** Demonstrates how multiple data sources can be integrated into a structured analytical workflow and how machine-learning outputs can be evaluated against historical results.

**Technologies:** Python, SQL, XGBoost, data visualization

<img src="ai-financial-signals-pipeline/images/cumulative_returns.png" alt="AI meta-signal strategy vs. buy-and-hold cumulative returns" width="700">

---

### [NYC Electricity Consumption & Cost Pipeline](./nyc-electricity-consumption-pipeline)

A data engineering and forecasting project analyzing electricity consumption and cost trends across New York City.

**Key features:**
- Integrates public data from **NYC Open Data** and the **New York Independent System Operator (NYISO)**
- Uses **dbt** to create development-, borough-, and city-level reporting datasets
- Compares NYCHA electricity consumption patterns with broader NYC grid demand
- Evaluates multiple forecasting approaches, including:
  - Linear Regression
  - Ridge Regression
  - Random Forest
  - Gradient Boosting
  - XGBoost
- Uses time-based validation to compare model performance

**Business value:** Demonstrates how public operational data can be transformed into reporting and forecasting tools for infrastructure, energy, and planning use cases.

**Technologies:** Python, SQL, dbt, machine learning, time-series analysis

<img src="nyc-electricity-consumption-pipeline/images/01_overview_metrics_trend.png" alt="NYC Electricity Consumption dashboard overview" width="700">

---

### [Portfolio RAG Pipeline](./portfolio-rag-pipeline)

A Retrieval-Augmented Generation (RAG) system that indexes the documentation across this portfolio and evaluates how different retrieval strategies affect answer quality.

Rather than building only a chatbot interface, this project focuses on **measuring whether the retrieval system actually works well**.

**Key features:**
- Creates local text embeddings using `sentence-transformers`
- Stores and searches embeddings using **DuckDB**
- Evaluates multiple document chunk sizes and retrieval depths
- Uses a manually developed benchmark set of 26 questions
- Measures:
  - Retrieval recall
  - Retrieval precision
  - Final answer correctness
- Includes an interactive Streamlit interface for querying the portfolio

The evaluation showed that the configuration with the highest retrieval precision was not the configuration producing the most accurate final answers. This demonstrates the importance of evaluating AI systems on end-user outcomes rather than relying on a single technical metric.

**Business value:** Demonstrates practical RAG architecture, experimentation, and evaluation methodology for enterprise knowledge-search and AI applications.

**Technologies:** Python, sentence-transformers, DuckDB, vector search, Streamlit, LLM evaluation

---

### [Retail Sales Analytics](./retail-sales-analytics)

A business-question-driven analysis of a 5,000-line-item retail transaction dataset, decomposing revenue into profitability, customer value, seasonality, geography, and fulfillment operations.

**Key features:**
- Recomputes every financial metric from primitives (cost, price, quantity, discount %) after showing the dataset's own supplied subtotal/total columns don't reconcile with unit economics on 99% of rows
- Full metrics suite: category profitability, discount-depth correlation, RFM customer segmentation, Pareto revenue concentration, year-over-year growth decomposition, geographic scale vs. customer quality, and fulfillment-speed testing
- Renders a validated, accessibility-checked chart set summarizing each finding

**Business value:** Demonstrates recomputing financial ground truth before analysis rather than trusting supplied aggregate fields, and decomposing a headline metric (e.g. revenue growth) into its underlying drivers instead of reporting it at face value. Headline finding: discount depth shows no measurable relationship to basket size or margin (|r| ≤ 0.02 on every measure), and two consecutive years grew revenue for structurally opposite reasons (more customers vs. bigger baskets).

**Technologies:** Python, pandas, matplotlib

---

## Technical Reference Projects

### [Cloud Platform Tool Index](./cloud-platform-tool-index)

A structured comparison of commonly used data and infrastructure services across **AWS, Google Cloud Platform, and Microsoft Azure**.

The project maps comparable services while also documenting where apparently similar products differ in architecture, cost structure, management model, and intended use.

Topics include:

- Object storage
- Relational databases
- Data warehouses
- Distributed data processing
- ETL services
- Workflow orchestration
- Streaming and messaging
- NoSQL databases
- Data catalogs and governance
- Identity and access management
- Serverless computing
- Container orchestration
- Secrets management
- Monitoring and observability

**Purpose:** Demonstrates familiarity with cloud architecture concepts and the ability to evaluate technology choices across platforms.

---

### [Machine Learning Algorithm Index](./machine-learning-algorithm-index) — In Development

A structured technical reference covering commonly used machine-learning and deep-learning methods.

Each entry includes:

- Conceptual overview
- Intuition and mathematical foundations
- Important hyperparameters
- Strengths and limitations
- Worked examples
- Runnable implementation examples
- Additional references

Topics include:

**Classical machine learning**
- Linear Regression
- Logistic Regression
- Decision Trees
- Random Forest
- Support Vector Machines
- K-Nearest Neighbors
- Naive Bayes
- Gradient Boosting
- XGBoost

**Unsupervised learning**
- K-Means Clustering
- Hierarchical Clustering
- Principal Component Analysis

**Deep learning and AI**
- Neural Networks
- Convolutional Neural Networks
- Recurrent Neural Networks
- LSTMs
- Large Language Models
- Retrieval-Augmented Generation

This project is currently under development and has not yet been published to GitHub.

---

## What This Portfolio Demonstrates

Taken together, these projects demonstrate experience with the full lifecycle of analytical data work:

**Data ingestion → transformation → modeling → validation → reporting**

They also highlight my ability to:

- Translate raw data into structured, usable datasets
- Design maintainable data pipelines
- Write analytical SQL and Python
- Build and evaluate machine-learning models
- Work with modern data-engineering tools
- Communicate technical results clearly
- Evaluate systems using measurable performance criteria
- Connect engineering decisions to analytical and business outcomes

My primary interests are in **data analytics, data science, data engineering, and data-oriented product development**.

---

## Contact

**James J. Pecore**

[LinkedIn](https://www.linkedin.com/in/james-j-pecore) | [GitHub](https://github.com/james-j-pecore)
