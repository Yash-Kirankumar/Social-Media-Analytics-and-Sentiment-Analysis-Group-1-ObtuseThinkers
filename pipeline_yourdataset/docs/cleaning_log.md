# Cleaning log

| What changed | Why |
|---|---|
| Removed exact duplicate order rows | Avoid counting the same exported order twice |
| Trimmed text columns | Remove accidental leading or trailing spaces |
| Parsed both `YYYY-MM-DD` and `DD.MM.YYYY` dates | The source exports use two date formats |
| Converted quantity and unit price to numbers | Required for validation and calculations |
| Converted March prices from cents to EUR | The March export stores prices in cents |
| Corrected `clara.schmidt(at)web.de` to `clara.schmidt@web.de` in memory | The supplied customer record has a malformed email |
| Corrected `Germny` to `Germany` in memory | The supplied customer record has a country typo |
| Quarantined rows with missing date, missing price, unknown customer or non-positive quantity | These are individual row issues and should not stop otherwise valid orders |
| Added customer name length, customer segment and future-date checks | Improve completeness and consistency before outputs are created |
| Added `revenue_by_category.csv` | Provide a category-level revenue summary |

The original files in `data/raw/` are not edited. The two customer corrections are applied in `clean_customers()` each time the pipeline runs.
