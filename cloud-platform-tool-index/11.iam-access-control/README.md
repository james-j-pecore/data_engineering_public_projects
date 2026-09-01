# IAM & Access Control

## Overview

The systems governing who (or what service) can do what to which resource — underpinning access to every other service in this index. Data engineers interact with this constantly: service roles for pipeline jobs, cross-service access grants (a Glue job reading S3, a Dataflow job writing BigQuery), and human access to sensitive data.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Identity + authorization | IAM (single combined product) | Cloud IAM (single combined product) | Entra ID (identity) + Azure RBAC (authorization) — two separate layers |
| Non-human identity | IAM roles / service accounts | Service accounts | Service principals / Managed Identities |
| Narrower identity-federation product | IAM Identity Center | Cloud Identity | (Entra ID itself covers this natively) |
| Predates the cloud platform / used outside it | No | No | Yes — Entra ID also serves Microsoft 365 and on-prem AD hybrid scenarios |

---

## What it's for

- **Granting pipeline jobs access to resources** — a Glue/Dataflow/ADF job needs a role/service account/managed identity with permission to read source data and write to a destination.
- **Human access control** — restricting which engineers/analysts can access which data, consoles, or resources.
- **Cross-service trust** — allowing one service to assume permissions to call another (e.g., a Lambda function reading from DynamoDB).

---

## Key differences

**Azure splits identity and authorization into two distinct products; AWS and GCP each combine them into one.** AWS IAM and GCP Cloud IAM are both resource-centric, policy-based systems where identities (users, roles, service accounts) and the policies granting them access to resources live in the same product. Azure separates this: **Entra ID** (formerly Azure AD) handles identity — users, groups, service principals, authentication, SSO, conditional access — as a genuinely standalone identity platform, while **Azure RBAC** handles authorization, assigning roles scoped to a subscription, resource group, or individual resource on top of Entra identities. This split is the single biggest conceptual difference in this category.

**Entra ID has no direct equivalent on AWS or GCP** because it isn't just a cloud-resource-access system — it's Microsoft's broader identity platform, also used for Microsoft 365 authentication and hybrid on-prem Active Directory synchronization. The closest AWS analog (IAM Identity Center) and GCP analog (Cloud Identity) are both narrower in scope, built specifically for federating access into the cloud platform rather than serving as a general-purpose enterprise identity provider. Organizations already standardized on Entra ID/Active Directory for corporate identity get a more unified story on Azure than replicating that setup on AWS or GCP.

**Non-human identity naming and mechanics differ but serve the same purpose** — AWS IAM roles, GCP service accounts, and Azure service principals/Managed Identities all let a service assume permissions without embedded long-lived credentials. Azure's Managed Identity specifically auto-manages credential rotation for you when attached to a resource (a VM, a Function), which is a slightly more turnkey version of the "assumed role" pattern than manually configuring an AWS IAM role's trust policy.

---

## When to reach for it vs. alternatives

- If your organization already runs on-prem Active Directory or Microsoft 365, Azure's Entra ID gives the most direct hybrid-identity story — worth weighing even independent of which cloud hosts the data workloads.
- Use Managed Identities (Azure) or IAM roles/service accounts (AWS/GCP) for all service-to-service access — never embed long-lived credentials in pipeline code regardless of provider.
- When designing cross-cloud pipelines, expect to maintain separate identity configuration per cloud — there's no native federation between AWS IAM, GCP IAM, and Entra ID without additional setup (e.g., workload identity federation).

---

## Resources

- [AWS IAM documentation](https://docs.aws.amazon.com/IAM/)
- [GCP Cloud IAM documentation](https://cloud.google.com/iam/docs)
- [Microsoft Entra ID documentation](https://learn.microsoft.com/en-us/entra/identity/) · [Azure RBAC documentation](https://learn.microsoft.com/en-us/azure/role-based-access-control/)
