from ryoma_ai.datasource.file import FileDataSource

f = FileDataSource("./creditcard.csv")

ds = f.to_arrow(format="csv")

ds.to_table()
