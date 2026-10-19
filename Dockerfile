# Imagem dos MCP servers (Python) + ferramentas de análise da Plena Alimentos
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código dos MCP servers + gerador de datasets
COPY .kiro/mcp-servers/ ./mcp-servers/

# Gera os CSVs no build (dados sintéticos determinísticos, seed fixa)
RUN python mcp-servers/plena-datasets/generate_datasets.py

# Por padrão sobe o MCP de business-rules (stdio). Sobrescreva o command no
# compose/run para rodar o de architecture, o seed do Postgres ou a análise.
CMD ["python", "mcp-servers/business-rules/server.py"]
