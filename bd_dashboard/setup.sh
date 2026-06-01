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

# 1. Subir MySQL
echo ""
echo "[1/4] Subindo MySQL..."
"${COMPOSE[@]}" up -d
echo "Aguardando MySQL iniciar..."
until docker exec prontuario_agil_bd_mysql mysql -uroot -proot123 -e "SELECT 1" > /dev/null 2>&1; do
    sleep 2
done
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
