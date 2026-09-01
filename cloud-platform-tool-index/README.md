# Cloud Platform Tool Index

A personal index of data engineering tools and services across AWS, GCP, and Azure. Each entry maps the equivalent service in every provider, explains what it's for, and calls out where the "equivalents" actually diverge in ways that matter when designing or migrating a pipeline.

## Purpose

- Provide a quick cross-cloud lookup: "I know X on AWS, what's the GCP/Azure equivalent?"
- Explain what each category of tool is *for*, not just name-match services.
- Flag meaningful differences between "equivalent" services (consistency models, pricing shape, serverless vs. managed, API ergonomics) so a 1:1 mapping isn't mistaken for a 1:1 replacement.

## How to use

- Skim the table below to find the category you need, then open that entry for the detailed comparison.
- Each entry is self-contained — no need to read them in order.

## Table of Contents

| # | Category | AWS | GCP | Azure |
|---|----------|-----|-----|-------|
| 1 | [Object Storage](1.object-storage/README.md) | S3 | Cloud Storage (GCS) | Blob Storage |
| 2 | Relational Database (OLTP) | RDS | Cloud SQL | Azure SQL Database |
| 3 | Data Warehouse (OLAP) | Redshift | BigQuery | Synapse Analytics |
| 4 | Distributed Batch Processing | EMR | Dataproc | HDInsight |
| 5 | Serverless ETL | Glue | Dataflow | Data Factory (Mapping Data Flows) |
| 6 | Workflow Orchestration | Managed Workflows for Apache Airflow (MWAA) | Cloud Composer | Data Factory (Pipelines) |
| 7 | Streaming / Pub-Sub Messaging | Kinesis Data Streams | Pub/Sub | Event Hubs |
| 8 | Stream Processing | Kinesis Data Analytics | Dataflow (streaming) | Stream Analytics |
| 9 | NoSQL Key-Value / Document | DynamoDB | Firestore | Cosmos DB |
| 10 | Data Catalog & Governance | Glue Data Catalog | Dataplex / Data Catalog | Purview |
| 11 | IAM & Access Control | IAM | Cloud IAM | Entra ID (Azure AD) + RBAC |
| 12 | Serverless Compute (Functions) | Lambda | Cloud Functions | Azure Functions |
| 13 | Container Orchestration | ECS / EKS | GKE | AKS |
| 14 | Secrets Management | Secrets Manager | Secret Manager | Key Vault |
| 15 | Monitoring & Observability | CloudWatch | Cloud Monitoring | Azure Monitor |

Only row 1 is written so far — the rest are planned categories. Rows will link out as entries are added.

---

## Per-entry template

Each category entry (`N.category-name/README.md`) follows this structure:

- **Overview** — what this category of tool does and why data engineers reach for it.
- **Comparison table** — AWS / GCP / Azure service name, side by side.
- **What it's for** — the core use case(s), in plain terms.
- **Key differences** — where the "equivalent" services actually diverge (consistency guarantees, pricing model, managed vs. serverless, API shape, limits). This is the section that matters most — service-name mapping alone is trivial and available in any cloud comparison chart; the differences are what actually affect a design decision.
- **When to reach for it vs. alternatives** — including cross-category alternatives on the same provider, if relevant (e.g., when S3 + Athena beats standing up Redshift).
- **Resources** — links to each provider's docs.
