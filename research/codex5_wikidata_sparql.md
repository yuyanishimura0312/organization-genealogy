# Codex 5: Wikidata SPARQL Query Set for Organization Genealogy

This query set extracts seed organization records from Wikidata for the long-term project "organization genealogy as living systems." It is designed for broad, iterative ETL rather than final authoritative classification.

License note: Wikidata data is available under CC0. Query files in this directory are intended to retrieve and transform CC0 Wikidata statements.

## Common Extraction Fields

All instance-oriented queries return these fields where available:

| Field | Wikidata property |
|---|---|
| `item` / `itemLabel` | entity QID and label |
| `creation_date` | inception, `P571` |
| `dissolution_date` | dissolved, abolished or demolished date, `P576` |
| `country` / `countryLabel` | country, `P17` |
| `located_in` / `located_inLabel` | location, `P276` |
| `parent_organization` / `parent_organizationLabel` | parent organization, `P749` |
| `instance_of` / `instance_ofLabel` | instance of, `P31` |
| `industry` / `industryLabel` | industry, `P452` |

The subclass-tree query returns class relationships for `Q43229` and includes the same property columns opportunistically, although most class items will not have them.

## Output Formats

Wikidata Query Service can return the same query as JSON or TSV by changing the HTTP `Accept` header:

- JSON: `Accept: application/sparql-results+json`
- TSV: `Accept: text/tab-separated-values`

For browser use, paste any `.sparql` file into Wikidata Query Service and use the result download menu. For ETL, call the endpoint with the query body and one of the headers above.

## Pagination Pattern

Every broad query includes `LIMIT` and `OFFSET`. Increase `OFFSET` by the same page size until a page returns fewer rows than `LIMIT`.

Recommended initial page size:

- broad organization queries: `LIMIT 5000`
- type-specific queries: `LIMIT 2000`
- subclass tree and count queries: no pagination needed, or `LIMIT 10000`

Date filters are written as inclusive lower bound and exclusive upper bound:

```sparql
FILTER(!BOUND(?creation_date) || (
  ?creation_date >= "1500-01-01T00:00:00Z"^^xsd:dateTime &&
  ?creation_date < "1800-01-01T00:00:00Z"^^xsd:dateTime
))
```

For ETL completeness, run both dated and undated passes. Wikidata has many organizations with missing or approximate inception dates.

## Query Inventory

| File | Purpose | Expected order of results |
|---|---:|---:|
| `00_organization_subclass_tree.sparql` | `Q43229` subclass tree | 1e3-1e4 |
| `01_corporation.sparql` | `Q188509` corporation seeds | 1e3-1e4 |
| `02_business.sparql` | `Q4830453` business seeds | 1e4-1e5 |
| `03_company.sparql` | `Q783794` company seeds | 1e5-1e6 |
| `04_multinational_corporation.sparql` | `Q161726` multinational corporation seeds | 1e3-1e4 |
| `05_kingdom.sparql` | `Q43702` kingdom seeds | 1e3-1e4 |
| `06_ethnic_group.sparql` | `Q41710` ethnic group seeds | 1e3-1e4 |
| `07_clan.sparql` | `Q11425700` clan seeds | 1e2-1e3 |
| `08_organization_general.sparql` | broad `Q43229` organization seeds | 1e6+ |
| `09_hanseatic_league_family.sparql` | Hanseatic League related seeds, `Q1530705` | 1e1-1e3 |
| `10_east_india_company_family.sparql` | East India Company related seeds, `Q2143665` | 1e1-1e3 |
| `11_monastic_order.sparql` | `Q210980` monastic order seeds | 1e2-1e3 |
| `12_religious_order.sparql` | `Q319608` religious order seeds | 1e2-1e3 |
| `13_monastery.sparql` | `Q44613` monastery seeds | 1e4-1e5 |
| `14_historical_organization.sparql` | `Q15243209` historical organization seeds | 1e4-1e5 |
| `15_decentralized_autonomous_organization.sparql` | `Q4287745` DAO seeds | 1e1-1e3 |
| `16_era_ancient.sparql` | ancient batch, -3000 to 500 CE | 1e3-1e4 |
| `17_era_medieval.sparql` | medieval batch, 500 to 1500 | 1e4-1e5 |
| `18_era_early_modern.sparql` | early modern batch, 1500 to 1800 | 1e4-1e5 |
| `19_era_modern.sparql` | modern batch, 1800 to 1945 | 1e5-1e6 |
| `20_era_contemporary.sparql` | contemporary batch, 1945 onward | 1e6+ |
| `21_region_continents.sparql` | continent batch via country continent `P30` | 1e5-1e6 |
| `22_region_major_countries.sparql` | major-country batch | 1e5-1e6 |
| `23_paginated_seed_template.sparql` | ETL pagination/date/type template | depends on parameters |
| `24_count_by_type.sparql` | rough volume and field coverage by major type | 1e1 |
| `25_enriched_all_major_types.sparql` | unified major-type extraction | 1e6+ |

## ETL Notes

Use `?item` as the stable key and preserve all returned QIDs, not only labels. Labels vary by language and can be missing. Treat the expected counts above as rough planning assumptions; the official endpoint changes over time and may time out for broad queries unless paginated.
