from pathlib import Path
import pandas as pd
import duckdb

# Dossier où se trouve le script Python
BASE_DIR = Path(__file__).parent

# Fichier Excel situé à côté du script
excel_file = BASE_DIR / "company_data.xlsx"

print(f"Script      : {Path(__file__).resolve()}")
print(f"Dossier     : {BASE_DIR}")
print(f"Fichier     : {excel_file}")
print(f"Existe      : {excel_file.exists()}")

if not excel_file.exists():
    raise FileNotFoundError(f"Fichier introuvable : {excel_file}")

# Liste des feuilles
xls = pd.ExcelFile(excel_file)

print("\nFeuilles disponibles :")
for sheet in xls.sheet_names:
    print(f" - {sheet}")
# Chargement de toutes les feuilles
sheets = pd.read_excel(excel_file, sheet_name=None)

# Connexion DuckDB
con = duckdb.connect()
# Enregistrement de chaque feuille comme table
for sheet_name, df in sheets.items():
    con.register(sheet_name, df)

print("\nTables DuckDB :")
print(con.sql("SHOW TABLES").df())

# Exemple de requête sur la feuille Employees
if "Employees" in sheets:
    print("\n=== Employés > 4000 € ===")
    result = con.sql(""" SELECT * FROM Employees WHERE Salaire > 4000 ORDER BY Salaire DESC """).df()
    print(result)
# Exemple : afficher le nombre de lignes de chaque feuille
print("\n=== Statistiques ===")
for sheet_name, df in sheets.items():
    print(f"{sheet_name:<30} : {len(df)} lignes")