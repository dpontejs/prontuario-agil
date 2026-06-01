import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root123"),
    "database": os.getenv("DB_NAME", "clinica_db"),
}

DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "data", "cnes", "BASE_DE_DADOS_CNES_202604"
)

UF_FILTRO = "24"  # RN


def load_csv(filename, usecols=None):
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path, sep=";", encoding="latin-1", dtype=str, usecols=usecols, quotechar='"')


def import_estabelecimentos(cursor):
    print("Carregando estabelecimentos...")
    df = load_csv("tbEstabelecimento202604.csv", usecols=[
        "CO_CNES", "NO_FANTASIA", "CO_ESTADO_GESTOR", "CO_MUNICIPIO_GESTOR", "CO_TIPO_ESTABELECIMENTO"
    ])

    df = df[df["CO_ESTADO_GESTOR"] == UF_FILTRO]
    print(f"  Estabelecimentos no RN: {len(df)}")

    # Carregar lookup de tipo de estabelecimento
    df_tipo = load_csv("tbTipoEstabelecimento202604.csv", usecols=[
        "CO_TIPO_ESTABELECIMENTO", "DS_TIPO_ESTABELECIMENTO"
    ])
    df = df.merge(df_tipo, on="CO_TIPO_ESTABELECIMENTO", how="left")

    # Carregar lookup de município
    df_mun = load_csv("tbMunicipio202604.csv", usecols=[
        "CO_MUNICIPIO", "NO_MUNICIPIO", "CO_SIGLA_ESTADO"
    ])
    df_mun = df_mun.rename(columns={"CO_MUNICIPIO": "CO_MUNICIPIO_GESTOR", "NO_MUNICIPIO": "municipio"})
    df = df.merge(df_mun[["CO_MUNICIPIO_GESTOR", "municipio"]], on="CO_MUNICIPIO_GESTOR", how="left")

    cursor.execute("DELETE FROM profissional_cnes")
    cursor.execute("DELETE FROM estabelecimento_cnes")

    sql = """INSERT INTO estabelecimento_cnes
             (cnes_codigo, nome_fantasia, tipo_estabelecimento, uf, municipio)
             VALUES (%s, %s, %s, %s, %s)"""

    df = df.fillna("")

    rows = []
    for _, row in df.iterrows():
        rows.append((
            str(row["CO_CNES"]).strip(),
            str(row.get("NO_FANTASIA", "")).strip(),
            str(row.get("DS_TIPO_ESTABELECIMENTO", "")).strip(),
            "RN",
            str(row.get("municipio", "")).strip(),
        ))

    cursor.executemany(sql, rows)
    print(f"  Inseridos: {len(rows)} estabelecimentos")
    return len(rows)


def import_profissionais(cursor):
    print("Carregando profissionais (carga horária)...")

    # Pegar os CO_CNES dos estabelecimentos já importados (RN)
    cursor.execute("SELECT id, cnes_codigo FROM estabelecimento_cnes")
    estab_map = {row[1]: row[0] for row in cursor.fetchall()}
    cnes_set = set(estab_map.keys())

    # Carregar carga horária — filtrar por estabelecimentos do RN via CO_UNIDADE
    # CO_UNIDADE = CO_MUNICIPIO (6 dígitos) + CO_CNES (7 dígitos)
    print("  Lendo tbCargaHorariaSus (pode demorar)...")
    df_ch = load_csv("tbCargaHorariaSus202604.csv", usecols=[
        "CO_UNIDADE", "CO_CBO", "QT_CARGA_HORARIA_AMBULATORIAL"
    ])

    # Extrair CO_CNES do CO_UNIDADE (últimos 7 dígitos)
    df_ch["CO_CNES"] = df_ch["CO_UNIDADE"].str[-7:]
    df_ch = df_ch[df_ch["CO_CNES"].isin(cnes_set)]
    print(f"  Vínculos no RN: {len(df_ch)}")

    # Carregar descrição do CBO
    df_cbo = load_csv("tbAtividadeProfissional202604.csv", usecols=[
        "CO_CBO", "DS_ATIVIDADE_PROFISSIONAL"
    ])
    df_ch = df_ch.merge(df_cbo, on="CO_CBO", how="left")

    df_ch["QT_CARGA_HORARIA_AMBULATORIAL"] = pd.to_numeric(
        df_ch["QT_CARGA_HORARIA_AMBULATORIAL"], errors="coerce"
    ).fillna(0).astype(int)

    sql = """INSERT INTO profissional_cnes
             (estabelecimento_cnes_id, nome, cbo, carga_horaria)
             VALUES (%s, %s, %s, %s)"""

    rows = []
    for _, row in df_ch.iterrows():
        estab_id = estab_map.get(row["CO_CNES"])
        if estab_id:
            rows.append((
                estab_id,
                "",  # nome não disponível nesta tabela
                row.get("DS_ATIVIDADE_PROFISSIONAL", row["CO_CBO"]),
                row["QT_CARGA_HORARIA_AMBULATORIAL"],
            ))

    # Inserir em lotes de 10000
    batch_size = 10000
    for i in range(0, len(rows), batch_size):
        cursor.executemany(sql, rows[i:i + batch_size])
        print(f"  Inseridos: {min(i + batch_size, len(rows))}/{len(rows)} profissionais")

    print(f"  Total inseridos: {len(rows)} profissionais")
    return len(rows)


def main():
    if not os.path.isdir(DATA_DIR):
        print(f"Diretório não encontrado: {DATA_DIR}")
        print("Extraia o ZIP do CNES em data/cnes/")
        return

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        import_estabelecimentos(cursor)
        conn.commit()
        import_profissionais(cursor)
        conn.commit()
        print("\nImportação concluída com sucesso!")

        # Verificação
        cursor.execute("SELECT COUNT(*) FROM estabelecimento_cnes")
        print(f"  Total estabelecimentos: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM profissional_cnes")
        print(f"  Total profissionais: {cursor.fetchone()[0]}")
    except Exception as e:
        conn.rollback()
        print(f"Erro na importação: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
