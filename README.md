# E-Commerce Data Quality Pipeline

Projeto de portfólio focado em **Engenharia de Dados Júnior**, desenvolvido a partir do problema de negócio proposto no Mini-Projeto 4 do curso *Fundamentos de Linguagem Python - Do Básico a Aplicações de IA*, da Data Science Academy.

> Este repositório não é uma cópia do notebook do curso. A proposta foi transformar o exercício de limpeza e análise de dados em um pequeno pipeline de dados modular, reproduzível, testável e documentado.

## Objetivo

Uma empresa de e-commerce possui dados transacionais com problemas de qualidade que comprometem análises de vendas e decisões de negócio. O pipeline recebe dados brutos contendo valores ausentes, duplicidades, tipos incorretos e outliers, aplica regras de transformação e validação e produz um dataset confiável para consumo analítico.

## Arquitetura

```text
Synthetic Source
      |
      v
data/raw/sales_raw.csv
      |
      v
[ Extract ]
      |
      v
[ Transform / Clean ]
      |
      v
[ Data Quality Validation ]
      |
      +------------------+
      |                  |
      v                  v
data/processed/       reports/
sales_clean.csv       analytical CSVs
      |
      v
Business-ready dataset
```

## Stack

- Python
- Pandas
- NumPy
- Pytest
- CSV
- Logging
- Git/GitHub

## Problemas de qualidade simulados

O conjunto de dados contém propositalmente:

- valores ausentes em `Quantidade`, `Status_Entrega` e `Cliente_ID`;
- três registros duplicados;
- `Preco_Unitario` armazenado como texto;
- um valor inválido em `Preco_Unitario`;
- `Cliente_ID` armazenado como texto;
- um outlier de quantidade igual a 50.

Esses problemas reproduzem o cenário proposto no mini-projeto original e permitem demonstrar tratamento sistemático de dados.

## Pipeline

### 1. Generate

`src/generate_data.py`

Gera o dataset sintético e injeta problemas de qualidade de forma reproduzível usando uma seed fixa.

### 2. Extract

`src/extract.py`

Carrega o CSV bruto e valida se todas as colunas obrigatórias estão presentes.

### 3. Transform

`src/transform.py`

Executa:

- conversão de tipos;
- tratamento de valores ausentes;
- remoção de linhas sem campos críticos;
- remoção de duplicatas;
- tratamento de outliers;
- criação da coluna `Total_Venda`;
- ordenação do dataset final.

### 4. Validate

`src/validate.py`

Valida regras mínimas de qualidade:

- ausência de pedidos duplicados;
- ausência de valores nulos;
- quantidade positiva;
- preço positivo;
- status de entrega dentro do domínio permitido;
- tipos corretos para data e valores monetários.

Se uma regra falhar, o pipeline é interrompido.

### 5. Analytics

`src/analytics.py`

Gera datasets analíticos com:

- receita total;
- receita por categoria;
- unidades vendidas por produto;
- receita por produto;
- vendas por dia;
- distribuição dos status de entrega.

## Estrutura do projeto

```text
ecommerce-data-quality-pipeline/
├── data/
│   ├── raw/
│   │   └── sales_raw.csv
│   └── processed/
│       └── sales_clean.csv
├── logs/
│   └── pipeline.log
├── reports/
│   ├── daily_sales.csv
│   ├── delivery_status.csv
│   ├── pipeline_metrics.json
│   ├── revenue_by_category.csv
│   ├── revenue_by_product.csv
│   └── units_by_product.csv
├── src/
│   ├── __init__.py
│   ├── analytics.py
│   ├── extract.py
│   ├── generate_data.py
│   ├── pipeline.py
│   ├── transform.py
│   └── validate.py
├── tests/
│   └── test_pipeline.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Como executar

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute o pipeline:

```bash
python -m src.pipeline
```

Execute os testes:

```bash
pytest -q
```

## Saídas

Após a execução, o pipeline gera:

- `data/raw/sales_raw.csv`: camada bruta;
- `data/processed/sales_clean.csv`: dataset limpo;
- `reports/*.csv`: agregações analíticas;
- `reports/pipeline_metrics.json`: métricas de execução e qualidade;
- `logs/pipeline.log`: histórico de execução.

## Conceitos de Engenharia de Dados demonstrados

Este projeto foi estruturado para demonstrar fundamentos importantes para uma posição de Engenharia de Dados Júnior:

- separação entre camada raw e processed;
- ingestão de dados;
- transformação com Pandas;
- data quality;
- schema validation;
- tratamento de erros;
- feature engineering;
- geração de datasets analíticos;
- observabilidade básica através de logs e métricas;
- modularização;
- testes automatizados;
- reprodutibilidade.

## Decisões técnicas

### Quantidade ausente

Valores ausentes são preenchidos com a mediana, pois ela é menos sensível a valores extremos.

### Status de entrega ausente

É utilizado o valor mais frequente da coluna.

### Cliente e preço ausentes/inválidos

Linhas sem `Cliente_ID` ou `Preco_Unitario` válidos são removidas, pois esses campos são críticos e não existe informação suficiente para inferi-los com segurança.

### Outliers

Valores de `Quantidade` acima de média + 3 desvios padrão são removidos, seguindo a regra usada no exercício-base.

## Próximas evoluções

Uma evolução natural deste projeto seria substituir arquivos CSV por PostgreSQL, adicionar orquestração e utilizar uma biblioteca dedicada de data quality. Essas melhorias foram deixadas fora desta primeira versão para manter o escopo coerente com um projeto de nível Júnior e facilitar a compreensão do pipeline.

## Origem acadêmica

O problema de negócio e a lógica-base de limpeza foram inspirados no Mini-Projeto 4 da Data Science Academy. A arquitetura do repositório, modularização, validações, logging, testes e organização em camadas foram adicionados para transformar o exercício em um projeto de portfólio de Engenharia de Dados.
