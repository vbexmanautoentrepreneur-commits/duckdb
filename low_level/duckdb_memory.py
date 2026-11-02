import duckdb
con = duckdb.connect()
con.execute(""" CREATE TABLE employees ( id INTEGER, nom VARCHAR, salaire INTEGER ) """)
con.execute(""" INSERT INTO employees VALUES (1, 'Alice', 3000), (2, 'Bob', 4500), (3, 'Charlie', 5500) """)
result = con.execute(""" SELECT * FROM employees WHERE salaire > 4000 """).fetchall()
print(result)