# Role → Document Access Mapping

## Roles
- Finance
- Marketing
- HR
- Engineering
- C-Level
- Employees

## Folder Structure (from Fintech-data)

- `Finance/` – financial reports, quarterly summaries…
- `marketing/` – campaign results, market analysis…
- `HR/` – employee-related CSV data…
- `engineering/` – technical architecture, processes…
- `general/` – general company docs, handbook, policies…

## Access Rules

- **Finance role**
  - Access: `Finance/`, `general/`
- **Marketing role**
  - Access: `marketing/`, `general/`
- **HR role**
  - Access: `HR/`, `general/`
- **Engineering role**
  - Access: `engineering/`, `general/`
- **Employee role**
  - Access: `general/` only
- **C-Level role**
  - Access: all folders (`Finance/`, `HR/`, `engineering/`, `marketing/`, `general/`)
