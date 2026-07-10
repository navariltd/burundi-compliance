# Burundi Compliance

## EBMS (Système de Facturation Électronique) Integration for ERPNext

## Introduction

Burundi Compliance has been designed to make compliance with Burundi tax
regulations simple, efficient, and reliable. To achieve this, it integrates
seamlessly with the EBMS (Electronic Billing Management System) APIs provided by
OBR (Office Burundais des Recettes), helping businesses automate recurring
compliance processes.

The app simplifies electronic invoicing, stock movement reporting, taxpayer
verification, and other regulatory requirements directly within ERPNext.

It builds on top of ERPNext and the Frappe Framework — powerful open-source
projects built and maintained by the team at Frappe Technologies.

---

# Key Features

## Electronic Invoice Submission

Automatically send Sales Invoices and POS Invoices to OBR for compliance and tax
reporting.

- Real-time invoice submission
- Invoice cancellation support
- Credit Note handling
- Deferred submission support
- Automatic retry handling

---

## Automated Stock Movement Tracking

Track inventory movements and synchronize stock transactions with OBR.

- Stock Entry tracking
- Purchase Receipt synchronization
- Delivery Note integration
- Automatic stock movement retries
- Bulk re-submission support

---

## Real-Time TIN Verification

Verify Customer, Supplier, and Company TINs directly against OBR services.

- Customer verification
- Supplier verification
- Company TIN confirmation
- Instant validation feedback

---

## Intelligent Retry & Queue Management

Failed requests are automatically retried in the background without interrupting
user workflows.

- Configurable retry attempts
- Retry delay management
- Scheduler-based synchronization
- Manual re-submission options
- Integration request logging

---

# Other Features

## Sandbox & Production Environment Support

Easily configure separate environments for testing and production deployments.

---

## Integration Request Monitoring

Track all API requests and responses using Integration Request logs.

- Request payloads
- Response payloads
- Error tracking
- Retry status
- API response monitoring

---

## Address Validation Support

Capture mandatory location information required by OBR.

- Rue
- Avenue
- Numero
- Commune
- Quartier
- Town
- Province

---

## Intelligent Background Processing

Schedulers automatically process pending invoice and stock synchronization
tasks.

---

# Quick Start

## Installation

For detailed installation and setup instructions, refer to the
[project documentation](https://docs.navari.co.ke/burundi-compliance).

---

# Manual Installation

## 1. Install Bench

Install Bench using the official guide:

https://docs.frappe.io/framework/user/en/installation

---

## 2. Install ERPNext

Install ERPNext using the official documentation:

https://github.com/frappe/erpnext#development-setup

---

## 3. Get the App

```bash
bench get-app --branch {branch-name} https://github.com/navariltd/burundi-compliance.git
```

---

## 4. Install the App

```bash
bench --site {sitename} install-app burundi_compliance
```

---

# Frappe Cloud Installation

1. Create a Bench
2. Create a Site
3. Select:
   - ERPNext
   - Burundi Compliance
4. Deploy the site

Within minutes, the system will be ready for use.

---

# Configuration

After installation:

1. Configure **EBMS Settings**
2. Add **API Endpoint URLs**
3. Configure **Sandbox or Production Environment**
4. Set retry and scheduler preferences
5. Configure Items for tracking
6. Begin invoice and stock synchronization

---

# Development

## Run Tests

```bash
bench --site sitename run-tests --app burundi_compliance
```

---

## Linting

```bash
pre-commit install
pre-commit run --all-files
```

---

# Troubleshooting

## Common Issues

### Failed Invoice Submission

Possible causes include:

- Invalid credentials
- OBR server downtime
- Network connectivity issues
- Invalid payload structure

---

## Retry Handling

The scheduler automatically retries failed requests using the retry settings
configured in EBMS Settings.

---

# Security

- Sandbox and production environments are isolated
- Credentials are securely stored within ERPNext
- Integration logs provide complete request auditing
- Failed requests are fully traceable

---

# Contributing

## Issue Guidelines

- Clearly describe the issue
- Include reproduction steps
- Attach relevant logs or screenshots

---

## Pull Request Requirements

- Follow project coding standards
- Add tests where applicable
- Ensure linting passes
- Write clear commit messages

---

# License

This project is licensed under GNU General Public License v3.

See:

https://github.com/navariltd/burundi-compliance/blob/develop/LICENSE
