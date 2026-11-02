import duckdb
from rich.console import Console
from rich.table import Table

console = Console()

result = duckdb.sql("""
    SELECT *
    FROM read_csv_auto('employees.csv')
    ORDER BY salary DESC
""").fetchall()

table = Table(title="👨‍💼 Employés")

table.add_column("ID", justify="center", style="cyan")
table.add_column("Nom", style="green")
table.add_column("Age", justify="right")
table.add_column("Service", style="yellow")
table.add_column("Salary", justify="right", style="magenta")

for row in result:
    table.add_row(
        str(row[0]),
        row[1],
        str(row[2]),
        row[3],
        f"{row[4]:,} €".replace(",", " ")
    )

console.print(table)