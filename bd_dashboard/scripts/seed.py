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


def corrigir_mojibake(valor):
    if not isinstance(valor, str) or ("Ã" not in valor and "Â" not in valor):
        return valor
    try:
        return valor.encode("latin1").decode("utf-8")
    except UnicodeError:
        return valor


def reparar_textos_utf8(cursor):
    campos_texto = {
        "medico": ["nome", "especialidade"],
        "paciente": ["nome", "email", "telefone"],
        "prontuario": ["notas_clinicas", "diagnostico", "prescricao"],
    }
    total_corrigido = 0

    for tabela, campos in campos_texto.items():
        cursor.execute(f"SELECT id, {', '.join(campos)} FROM {tabela}")
        for row in cursor.fetchall():
            registro_id = row[0]
            valores_corrigidos = []
            campos_corrigidos = []

            for campo, valor in zip(campos, row[1:]):
                valor_corrigido = corrigir_mojibake(valor)
                if valor_corrigido != valor:
                    campos_corrigidos.append(campo)
                    valores_corrigidos.append(valor_corrigido)

            if campos_corrigidos:
                set_clause = ", ".join(f"{campo}=%s" for campo in campos_corrigidos)
                cursor.execute(
                    f"UPDATE {tabela} SET {set_clause} WHERE id=%s",
                    (*valores_corrigidos, registro_id),
                )
                total_corrigido += 1

    if total_corrigido:
        print(f"Textos com acentuação corrigidos: {total_corrigido} registros.")


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

    reparar_textos_utf8(cursor)
    conn.commit()

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
