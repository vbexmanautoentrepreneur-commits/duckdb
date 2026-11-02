import duckdb
import pandas as pd

# Données
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 35, 42],
    "salary": [3000, 4500, 5500]
})
#pandas transform Dico in Table like Database
print(df)
# Request SQL directly on Dataframe pandas
result = duckdb.sql(""" SELECT name, salary, age FROM df WHERE age > 30 ORDER BY salary DESC """).df()
print(result)
