# Workflow Orchestration

## Overview

Orchestration tools schedule, sequence, and monitor multi-step pipelines — DAGs of tasks with dependencies, retries, and alerting — tying together the other services in this index (extract from a database, transform in Spark, load into a warehouse) into one managed, observable workflow.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | Managed Workflows for Apache Airflow (MWAA) | Cloud Composer | Data Factory (Pipelines) |
| Underlying engine | Apache Airflow | Apache Airflow | Proprietary (Azure's own orchestration engine) |
| DAG definition | Python (Airflow DAGs) | Python (Airflow DAGs) | JSON pipeline definitions (authored visually or via SDK) |
| Portable to other clouds | Yes — standard Airflow DAGs | Yes — standard Airflow DAGs | No — ADF pipeline definitions are Azure-specific |

---

## What it's for

- **Cross-service pipeline scheduling** — running "extract → transform → load" (or more complex DAGs) on a schedule or trigger, with dependency management between steps.
- **Retry and alerting logic** — built-in handling for step failures, retries, backfills, and SLA monitoring.
- **Cross-cloud/cross-tool coordination** — orchestrators typically call out to whatever services actually do the work (Glue/Dataflow/ADF jobs, warehouse loads, external APIs), acting as the control plane rather than the compute.

---

## Key differences

**MWAA and Cloud Composer are literally the same open-source project underneath.** Both are managed Apache Airflow — same DAG-authoring model, same Python-based task definitions, same operator ecosystem. This means Airflow DAGs are largely portable between AWS and GCP with mostly configuration-level changes (connection strings, IAM roles), not a rewrite. Practical differences between MWAA and Composer come down to networking model (VPC setup, private/public endpoints), environment sizing and autoscaling behavior, and how each integrates with its cloud's native IAM and logging — not the orchestration model itself.

**Data Factory Pipelines is not Airflow, and is not portable.** ADF has its own proprietary orchestration engine with a JSON-based pipeline definition format, authored either visually in the ADF Studio UI or via SDK/ARM templates. Conceptually it covers the same ground (DAGs, dependencies, scheduling, retries, triggers) but the DAGs themselves are not code-compatible with Airflow — migrating a pipeline from ADF to Airflow-based orchestration (or vice versa) means re-authoring it, not just redeploying it. This is one of the more consequential platform-lock-in points across this whole index, since orchestration logic tends to accumulate significant business logic over time.

**Azure does now also offer managed Airflow** via Workflow Orchestration Manager (built on top of Data Factory), narrowing this gap for teams that specifically want Airflow on Azure rather than native ADF pipelines — worth checking current availability/maturity if Airflow portability matters for your team.

**Authoring philosophy mirrors the ETL split** — Airflow (MWAA/Composer) is code-first Python, while ADF pipelines default to a visual designer (with a JSON/SDK authoring path available for those who want it), matching the same code-first-vs-visual pattern seen in [Serverless ETL](../5.serverless-etl/README.md).

---

## When to reach for it vs. alternatives

- Reach for Airflow (MWAA/Composer) when DAG portability across clouds matters, when the team already has Airflow expertise, or when you need Airflow's large operator/provider ecosystem for third-party integrations.
- Reach for ADF Pipelines when you're Azure-native and want tight integration with ADF's own Mapping Data Flows and the broader Azure ecosystem, or prefer visual pipeline authoring.
- Consider Azure's managed-Airflow offering specifically when you want Airflow's portability/ecosystem while staying on Azure.

---

## Resources

- [AWS MWAA documentation](https://docs.aws.amazon.com/mwaa/)
- [GCP Cloud Composer documentation](https://cloud.google.com/composer/docs)
- [Azure Data Factory documentation](https://learn.microsoft.com/en-us/azure/data-factory/)
- [Apache Airflow documentation](https://airflow.apache.org/docs/)
