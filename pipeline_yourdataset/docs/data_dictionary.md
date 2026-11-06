# Data dictionary

All monetary values are in EUR. Dates use `YYYY-MM-DD` in the cleaned output.

## `fct_orders.csv`

| Column | Meaning | Source / calculation |
|---|---|---|
| `order_id` | Unique order identifier | Raw order file; one capital letter and three digits |
| `order_date` | Order date | Raw date parsed from ISO or `DD.MM.YYYY`; missing values are quarantined |
| `customer_id` | Customer identifier | Must match a customer in `customers.csv` |
| `category` | Product category | `Accessories` or `Electronics` |
| `quantity` | Number of items | Numeric; must be positive for trusted rows |
| `unit_price` | Price per item | Numeric EUR; March source prices are divided by 100 |
| `source_file` | Original order filename | Added during loading; used for lineage and March price correction |
| `city` | Customer city | Joined from `customers.csv` |
| `line_total` | Total value of the order line | `quantity * unit_price`, rounded to 2 decimals |

## `quarantine_orders.csv`

Contains the cleaned order columns above plus:

| Column | Meaning |
|---|---|
| `reason` | Why the row was held back: missing order date, missing unit price, unknown customer, or quantity less than or equal to zero |

## `revenue_by_city.csv`

| Column | Meaning |
|---|---|
| `city` | Customer city |
| `line_total` | Sum of trusted order line totals for the city, EUR |

## `revenue_by_category.csv` (new output)

| Column | Meaning |
|---|---|
| `category` | Product category |
| `line_total` | Sum of trusted order line totals for the category, EUR |

## Input columns

`orders_*.csv` contains `order_id`, `order_date`, `customer_id`, `category`, `quantity`, and `unit_price`. `customers.csv` contains `customer_id`, `customer_name`, `city`, `country`, `email`, and `segment`.
