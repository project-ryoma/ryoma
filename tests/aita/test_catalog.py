from aita.datasource.catalog import Catalog

data = {
    "catalog_name": "main",
    "databases": [
        {
            "database_name": "",
            "tables": [
                {
                    "table_name": "author",
                    "columns": [
                        {"name": "aid", "type": "INT", "nullable": 1},
                        {"name": "homepage", "type": "TEXT", "nullable": 1},
                        {"name": "name", "type": "TEXT", "nullable": 1},
                        {"name": "oid", "type": "INT", "nullable": 1},
                    ],
                }
            ],
        }
    ],
}


def test_catalog_model():
    catalog = Catalog(**data)
    assert catalog.catalog_name == "main"
    assert len(catalog.databases) == 1
    assert catalog.databases[0].database_name == ""
    assert len(catalog.databases[0].tables) == 1
