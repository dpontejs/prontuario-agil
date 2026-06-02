import os
import sys
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root123"),
    "database": os.getenv("DB_NAME", "clinica_db"),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
}


def run_sql_file(cursor, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement and not statement.upper().startswith(("CREATE DATABASE", "USE")):
            cursor.execute(statement)


def main():
    sql_dir = os.path.join(os.path.dirname(__file__), "..", "sql")

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("Criando tabelas...")
    run_sql_file(cursor, os.path.join(sql_dir, "01_create_tables.sql"))
    conn.commit()

    print("Criando views...")
    run_sql_file(cursor, os.path.join(sql_dir, "02_create_views.sql"))
    conn.commit()

    print("Inserindo dados iniciais...")
    try:
        run_sql_file(cursor, os.path.join(sql_dir, "03_seed_data.sql"))
        conn.commit()
        print("Seed inserido com sucesso!")
    except mysql.connector.errors.IntegrityError:
        conn.rollback()
        print("Dados já existem (seed já foi executado).")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
