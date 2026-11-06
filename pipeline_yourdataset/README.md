# Shop pipeline

A small, repeatable pipeline that turns the monthly shop order files into trusted order data and revenue summaries.

## Group members

- A. Saarthak Joshi
- B. Vivek Attri
- C. Yash Kirankumar
- D. Bhaskaran Brindavan
- E. Nandeesh Venkatapura Siddaraju

## Run it

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python pipeline.py
```

Each run adds a result block to `logs/run_log.txt`. The raw files in `data/raw/` are read only.

## Project structure

```text
pipeline_yourdataset/
├── data/
│   ├── raw/                 Original monthly orders and customer file
│   └── output/              Generated CSV files
├── docs/
│   ├── data_dictionary.md
│   ├── cleaning_log.md
│   ├── lineage.md
│   └── lineage.png
├── extras/                  Extra April sample file
├── logs/run_log.txt
├── pipeline.py
├── rules.py
└── requirements.txt
```

## Pipeline steps

1. **Load:** read all `orders_*.csv` files and `customers.csv`. Add `source_file` to each order.
2. **Clean:** remove exact duplicate rows, trim text, parse ISO and German date formats, and convert numeric columns.
3. **Correct known customer typos:** change the supplied invalid email for Clara to `clara.schmidt@web.de` and `Germny` to `Germany`. These changes happen in memory; the raw CSV is not overwritten.
4. **Validate:** apply the critical checks in `rules.py`. A failed critical check stops the run before output files are written.
5. **Split:** move row-level issues (missing date, missing price, unknown customer, non-positive quantity) to quarantine.
6. **Enrich:** add the customer's city and calculate `line_total`.
7. **Output:** write the fact table, quarantine table, revenue by city and revenue by category.

## Validation rules added for this exercise

The project keeps the email and country checks from Lab 3.2 and adds these three checks:

| New rule | Check | Why |
|---|---|---|
| Customer name | At least 2 characters | Avoid blank or unusable names |
| Customer segment | `Private` or `Business` | Keep segment values consistent |
| Order date | Must not be later than today's date (custom check) | Prevent future-dated orders |

The existing order ID, category, customer ID, email and country checks remain in place. Missing order dates are allowed through schema validation so that the row can be placed in quarantine.

## Outputs

- `fct_orders.csv`: trusted order lines with customer city and calculated `line_total`.
- `quarantine_orders.csv`: rows held back, with a `reason`.
- `revenue_by_city.csv`: sum of trusted `line_total` by city.
- `revenue_by_category.csv`: sum of trusted `line_total` by product category.

Column definitions and units are in [`docs/data_dictionary.md`](docs/data_dictionary.md). Cleaning decisions are in [`docs/cleaning_log.md`](docs/cleaning_log.md). The flow is in [`docs/lineage.md`](docs/lineage.md) and [`docs/lineage.png`](docs/lineage.png).

## Git versioning

Example commit sequence:

```bash
git init
git add rules.py pipeline.py
git commit -m "feat: add customer and date validation rules"

git add data/output/revenue_by_category.csv
git commit -m "feat: add revenue by category output"

git add README.md docs logs data
git commit -m "docs: document pipeline, cleaning and lineage"

git branch -M main
git remote add origin https://github.com/GROUP/REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your group's GitHub repository. Include the run log and lineage drawing in the repository. Set the repository to public or add the lecturer as a collaborator.
