from aita.datasource.catalog import Catalog

data = {
    "catalog_name": "main",
    "catalog_db_schemas": [
        {
            "db_schema_name": "",
            "db_schema_tables": [
                {
                    "table_name": "author",
                    "table_type": "table",
                    "table_columns": [
                        {"column_name": "aid", "xdbc_type_name": "INT", "xdbc_nullable": 1},
                        {"column_name": "homepage", "xdbc_type_name": "TEXT", "xdbc_nullable": 1},
                        {"column_name": "name", "xdbc_type_name": "TEXT", "xdbc_nullable": 1},
                        {"column_name": "oid", "xdbc_type_name": "INT", "xdbc_nullable": 1},
                    ],
                }
            ],
        }
    ],
}


def test_catalog_model():
    catalog = Catalog(**data)
    assert catalog.catalog_name == "main"
    assert len(catalog.catalog_db_schemas) == 1
    assert catalog.catalog_db_schemas[0].db_schema_name == ""
    assert len(catalog.catalog_db_schemas[0].db_schema_tables) == 1
