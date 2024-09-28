from ryoma_ai.datasource.metadata import Catalog

data = {
    "catalog_name": "main",
    "schemas": [
        {
            "schema_name": "",
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
    assert len(catalog.schemas) == 1
    assert catalog.schemas[0].schema_name == ""
    assert len(catalog.schemas[0].tables) == 1
