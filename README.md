# Dashboard Temperaturas Diárias - Geocalor

Dashboard leve e independente para visualização de temperaturas diárias e umidade.

## Características

- Visualização de temperaturas (máxima, média, mínima)
- Visualização de umidade
- Mapa interativo com estações meteorológicas
- Filtros por cidade e período
- Metodologia EHF explicada

## Requisitos

- Python 3.11+
- Docker (opcional)
- Arquivo de dados: `data/temp.xlsx` ou `processed/temp.parquet`

## Instalação Local

```bash
pip install -r requirements.txt
python app.py
```

## Executar com Docker

```bash
docker build -t dashboard-temperaturas .
docker run -p 8050:8050 dashboard-temperaturas
```

## Estrutura

```
dashboard-temperaturas/
├── app.py              # Aplicação principal
├── data_processing.py  # Processamento de dados
├── visualization.py    # Funções de visualização
├── config_paths.py     # Configuração de caminhos
├── cache_manager.py    # Gerenciador de cache
├── assets/             # Imagens e CSS
├── data/               # Dados originais (Excel/CSV)
├── processed/         # Dados processados (Parquet)
├── cache/              # Cache de dados processados
├── requirements.txt    # Dependências Python
├── Dockerfile         # Configuração Docker
└── README.md          # Este arquivo
```
