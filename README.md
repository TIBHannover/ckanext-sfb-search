# ckanext-sfb-search

This CKAN extension adds search modes for information that CKAN does not index
in its standard dataset search. It also derives dataset tags from annotated
CSV and XLSX uploads.

## Compatibility

| CKAN version | Status |
| --- | --- |
| 2.11 | Supported and tested with Python 3.10 |
| 2.10 | Supported and tested with Python 3.10 |
| 2.9 and earlier | Not supported |

The package requires Python 3.9 or newer.

## How it works

The package exposes two CKAN plugins:

- `auto_tag` reads column information from uploaded CSV and XLSX resources.
  Annotated files use their first data row as tag names; ordinary files use
  their column headers. Tags are added with CKAN's `package_patch` action.
- `sfb_search` stores uploaded resource column names in the
  `data_resource_column_index` table and extends dataset search with prefixed
  queries. It also highlights resources matched by column or metadata search.

Supported query prefixes are:

| Query | Searches |
| --- | --- |
| `column:temperature` | Indexed CSV/XLSX column names |
| `sample:sample-name` | Samples supplied by the optional `sample_link` plugin |
| `publication:author` | Citations supplied by the optional `dataset_reference` plugin |
| `material_combination:steel` | Resource material metadata |
| `surface_preparation:polished` | Resource preparation metadata |
| `atmosphere:argon` | Resource atmosphere metadata |
| `data_type:mechanical` | Resource data-type metadata |
| `analysis_method:xrd` | Resource analysis-method metadata |

The `/sfb_search/indexer` route rebuilds the column index for existing
resources. It is restricted to sysadmins.

## Installation

1. Activate the CKAN virtual environment.
2. Clone and install the extension and its dependencies:

       git clone https://github.com/TIBHannover/ckanext-sfb-search.git
       cd ckanext-sfb-search
       pip install -r requirements.txt
       pip install -e .

3. Add both plugins to `ckan.plugins`:

       ckan.plugins = ... auto_tag sfb_search

4. Create or upgrade the extension database table:

       ckan -c /etc/ckan/default/ckan.ini db upgrade -p sfb_search

5. Restart CKAN.

Run the migration whenever the extension is upgraded. Existing installations
can rebuild their resource-column index by requesting `/sfb_search/indexer` as
a sysadmin.

## Tests

Install `dev-requirements.txt`, then run:

    pytest --ckan-ini=test.ini --cov=ckanext.sfb_search_extension ckanext/sfb_search_extension

The GitHub Actions matrix and `docker-compose.ci.yml` run the suite against
CKAN 2.10 and 2.11.

## License

[AGPL](LICENSE)
