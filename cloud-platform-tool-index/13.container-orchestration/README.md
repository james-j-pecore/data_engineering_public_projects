# Container Orchestration

## Overview

Managed platforms for running containerized workloads at scale — increasingly common in data engineering for packaging custom transformation logic, ML training/serving, or microservices supporting a pipeline, where a fully managed serverless option doesn't fit but running Kubernetes yourself is more operational overhead than wanted.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Kubernetes offering | EKS | GKE | AKS |
| Proprietary (non-K8s) alternative | ECS | — | — |
| Serverless container option | Fargate (works with both ECS and EKS) | Cloud Run / GKE Autopilot | Azure Container Instances / AKS with virtual nodes |
| Control plane pricing | Per-cluster fee | Per-cluster fee (with free tier) | Free — pay only for nodes |

---

## What it's for

- **Custom containerized processing jobs** — packaging transformation logic with specific dependencies that don't fit cleanly into a managed ETL service's environment.
- **ML model training and serving infrastructure** — often containerized for reproducibility and portability across environments.
- **Long-running services supporting a data platform** — internal APIs, custom connectors, or monitoring tooling.

---

## Key differences

**AWS uniquely offers two distinct container orchestrators**, giving a real choice between platforms. **ECS** is AWS's own proprietary, simpler scheduler — deeply integrated with the rest of AWS and easier to reason about if you don't need Kubernetes specifically — while **EKS** is managed Kubernetes for teams wanting the open, portable K8s API and ecosystem. GCP and Azure each offer only the Kubernetes path (GKE, AKS) as their primary managed container platform, without a proprietary non-K8s alternative at the same tier.

**GKE is the most mature managed Kubernetes offering**, unsurprising given Google originated Kubernetes internally (as the successor to Borg) before open-sourcing it — GKE's **Autopilot** mode in particular offers the most hands-off, fully-managed node experience of the three, where GCP manages node provisioning and sizing automatically rather than just the control plane.

**AKS is free at the control-plane level**, where EKS charges a per-cluster-hour fee for the control plane regardless of node usage (GKE also charges a per-cluster fee, with one free zonal cluster per billing account). This is a straightforward cost difference for smaller or numerous-cluster setups, though for most production workloads node costs dominate the bill regardless of provider.

**Serverless container options differ in shape.** Fargate lets you run ECS or EKS workloads without managing the underlying EC2 instances at all — a genuinely serverless layer on top of either AWS orchestrator. Cloud Run serves a similar serverless-container niche on GCP but as a standalone product rather than a mode of GKE (GKE Autopilot is GCP's closer analog to "serverless-feeling Kubernetes"). Azure's equivalents (Container Instances, AKS virtual nodes) are comparatively less commonly reached for as the default serverless-container choice.

---

## When to reach for it vs. alternatives

- Reach for ECS over EKS on AWS when you don't specifically need Kubernetes-ecosystem portability or tooling — it's simpler to operate for AWS-only workloads.
- Reach for a managed Kubernetes offering (EKS/GKE/AKS) when portability across clouds or on-prem, or the broader K8s ecosystem (Helm charts, operators, existing manifests), matters.
- Reach for the serverless-container layer (Fargate, Cloud Run, GKE Autopilot) when you want container packaging without any node-level capacity planning at all.

---

## Resources

- [AWS ECS documentation](https://docs.aws.amazon.com/ecs/) · [AWS EKS documentation](https://docs.aws.amazon.com/eks/)
- [GCP GKE documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Azure AKS documentation](https://learn.microsoft.com/en-us/azure/aks/)
