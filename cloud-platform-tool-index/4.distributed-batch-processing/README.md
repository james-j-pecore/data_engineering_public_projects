# Distributed Batch Processing

## Overview

Managed Hadoop/Spark clusters for large-scale batch data processing — the "bring your own cluster" tier between fully serverless ETL and running open-source big-data tooling yourself on raw VMs. You still think in terms of clusters, nodes, and jobs, but the provider handles provisioning, patching, and (to varying degrees) scaling.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | EMR (Elastic MapReduce) | Dataproc | HDInsight |
| Cluster startup time | Minutes | ~90 seconds (fastest of the three) | Minutes |
| Serverless variant | EMR Serverless | Dataproc Serverless | — (typically Synapse Spark pools or Databricks instead) |
| Common alternative on this cloud | — | — | Synapse Spark pools / Azure Databricks (both more commonly recommended today) |

---

## What it's for

- **Large-scale Spark/Hadoop/Hive/Presto jobs** — heavy transformations, joins, and aggregations over datasets too large or complex for serverless ETL tools to handle efficiently.
- **Migrating existing on-prem Hadoop workloads** to the cloud with minimal rewrite — all three support the standard Hadoop ecosystem (Hive, HBase, Presto/Trino, Spark) more or less as-is.
- **Custom cluster configurations** — when you need specific Spark tuning, custom libraries, or cluster topologies that fully-managed serverless ETL tools don't expose.

---

## Key differences

**Dataproc is the fastest to spin up and tear down**, historically around 90 seconds versus several minutes for EMR or HDInsight, and bills per-second — this makes ephemeral, job-scoped clusters (spin up, run one job, tear down) far more practical on Dataproc than on the others, where the startup overhead makes long-lived clusters more common in practice.

**EMR is the most feature-rich and ecosystem-integrated**, with the deepest integration into the rest of AWS (S3 as native storage, Glue Data Catalog as metastore, IAM-based fine-grained access) and the broadest set of supported open-source frameworks. It's the most mature of the three and the one most large enterprises with heavy AWS footprints default to.

**HDInsight is increasingly the least-recommended default on its own cloud.** Many Azure-based data teams reach for Synapse Spark pools (integrated into the Synapse workspace alongside the warehouse) or Azure Databricks (a first-party-supported partnership product) instead of HDInsight for new Spark work — HDInsight remains most relevant for non-Spark Hadoop-ecosystem components (HBase, Kafka via HDInsight) or migrating existing on-prem Hadoop deployments where API compatibility with open-source Hadoop matters more than tight Azure-native integration.

**Serverless variants close some of the gap** — EMR Serverless and Dataproc Serverless both let you run Spark jobs without managing cluster lifecycle at all, closer to how Glue and Dataflow work, but still expose Spark-specific tuning knobs that fully-abstracted ETL services don't.

---

## When to reach for it vs. alternatives

- Reach for this tier when you need Spark/Hadoop-ecosystem-specific tools (Hive, HBase, Presto/Trino) or fine-grained cluster control that serverless ETL (Glue/Dataflow/ADF) doesn't expose.
- Prefer the serverless variant (EMR Serverless, Dataproc Serverless) when jobs are intermittent and you don't want to manage cluster scaling/teardown yourself.
- On Azure, default to Synapse Spark pools or Databricks over HDInsight for new Spark-centric work; reach for HDInsight specifically when migrating an existing Hadoop-ecosystem workload or needing components (HBase, Kafka) that aren't well-covered elsewhere in Azure's stack.

---

## Resources

- [AWS EMR documentation](https://docs.aws.amazon.com/emr/)
- [GCP Dataproc documentation](https://cloud.google.com/dataproc/docs)
- [Azure HDInsight documentation](https://learn.microsoft.com/en-us/azure/hdinsight/)
