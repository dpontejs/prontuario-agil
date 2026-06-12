#!/bin/bash
set -e

cd "$(dirname "$0")"

if docker compose version > /dev/null 2>&1; then
    COMPOSE=(docker compose)
elif command -v docker-compose > /dev/null 2>&1; then
    COMPOSE=(docker-compose)
else
    echo "Docker Compose não encontrado. Instale o plugin 'docker compose' ou o binário 'docker-compose'."
    exit 1
fi

echo "=== Setup do Prontuário Ágil — Dashboard BD ==="

MYSQL_CONTAINER="prontuario_agil_bd_mysql"
MYSQL_HOST="${DB_HOST:-127.0.0.1}"
MYSQL_PORT="${DB_PORT:-3306}"
MYSQL_USER="${DB_USER:-root}"
MYSQL_PASSWORD="${DB_PASSWORD:-root123}"
MYSQL_DATABASE="${DB_NAME:-clinica_db}"
RECREATED_MYSQL=0

export DB_HOST="$MYSQL_HOST"
export DB_PORT="$MYSQL_PORT"
export DB_USER="$MYSQL_USER"
export DB_PASSWORD="$MYSQL_PASSWORD"
export DB_NAME="$MYSQL_DATABASE"

wait_for_mysql_container() {
    until docker exec "$MYSQL_CONTAINER" mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" > /dev/null 2>&1; do
        sleep 2
    done
}

wait_for_mysql_host_port() {
    python3 - "$MYSQL_HOST" "$MYSQL_PORT" <<'PY'
import socket
import sys
import time

host = sys.argv[1]
port = int(sys.argv[2])
deadline = time.time() + 60

while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            sys.exit(0)
    except OSError:
        time.sleep(2)

sys.exit(1)
PY
}

ensure_mysql_port_published() {
    local port_config
    port_config="$(docker inspect -f '{{range $p, $conf := .NetworkSettings.Ports}}{{if eq $p "3306/tcp"}}{{json $conf}}{{end}}{{end}}' "$MYSQL_CONTAINER" 2>/dev/null)"
    if [ -z "$port_config" ] || [ "$port_config" = "null" ]; then
        echo "Container MySQL sem porta 3306 publicada no host. Recriando serviço..."
        "${COMPOSE[@]}" up -d --force-recreate mysql
        RECREATED_MYSQL=1
    fi
}

# 1. Subir MySQL
echo ""
echo "[1/4] Subindo MySQL..."
"${COMPOSE[@]}" up -d
echo "Aguardando MySQL iniciar..."
wait_for_mysql_container
ensure_mysql_port_published
if [ "$RECREATED_MYSQL" -eq 1 ]; then
    wait_for_mysql_container
fi
if ! wait_for_mysql_host_port; then
    echo "ERRO: MySQL respondeu no container, mas não em ${MYSQL_HOST}:${MYSQL_PORT}."
    echo "Verifique se a porta ${MYSQL_PORT} está livre no host ou ajuste DB_PORT antes de executar o setup."
    exit 1
fi
echo "MySQL pronto."

# 2. Criar venv e instalar dependências
echo ""
echo "[2/4] Instalando dependências Python..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q

# 3. Criar tabelas e seed
echo ""
echo "[3/4] Criando tabelas e inserindo dados iniciais..."
python scripts/seed.py

# 4. Verificar dados CNES
echo ""
echo "[4/4] Verificando dados CNES..."
if [ -d "data/cnes/BASE_DE_DADOS_CNES_202604" ]; then
    echo "Dados CNES encontrados. Importando..."
    python scripts/import_csv.py
else
    echo "AVISO: Dados CNES não encontrados."
    echo "Baixe o arquivo em:"
    echo "  https://cnes.datasus.gov.br/EstatisticasServlet?path=BASE_DE_DADOS_CNES_202604.ZIP"
    echo "Extraia em bd_dashboard/data/cnes/ e execute: cd bd_dashboard && python scripts/import_csv.py"
fi

echo ""
echo "=== Setup concluído! ==="
echo "Execute: cd bd_dashboard && source venv/bin/activate && streamlit run app/inicio.py"
