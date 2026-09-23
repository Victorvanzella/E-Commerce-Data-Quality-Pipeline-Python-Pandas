# Runbook de operação

## Execução normal

```bash
python -m src.pipeline
python -m src.verify_outputs
```

Uma execução bem-sucedida retorna código `0`, grava métricas com status `SUCCESS` e mostra 12 regras aprovadas no dataset processado.

## Configuração

Copie `.env.example` para `.env` se precisar alterar os padrões:

| Variável | Padrão | Finalidade |
|---|---:|---|
| `SOURCE_ROW_COUNT` | 10000 | quantidade de pedidos válidos gerados |
| `SOURCE_SEED` | 42 | reprodutibilidade da fonte |
| `QUALITY_MIN_ACCEPTANCE_RATE` | 99.0 | taxa mínima para o quality gate |

## Processar uma fonte externa

1. coloque o arquivo em `data/raw/sales_orders_raw.csv`;
2. confirme as 13 colunas de `contracts/sales_orders.yml`;
3. execute `python -m src.pipeline --skip-generate`;
4. confira `data/quarantine` e `reports/data_quality_report.json`.

## Diagnóstico

| Sintoma | Verificação | Ação |
|---|---|---|
| coluna obrigatória ausente | mensagem `SchemaContractError` | corrigir o produtor ou versionar o contrato |
| quality gate reprovado | taxa no relatório de qualidade | analisar motivos e volume da quarentena |
| schema Pandera reprovado | detalhes de `SchemaErrors` no log | conferir tipo/domínio na transformação |
| contagem inesperada | `pipeline_metrics.json` | comparar raw, accepted e quarantined |
| execução não reproduzível | seed e quantidade configuradas | fixar `.env` ou argumentos da CLI |

## Evidências

- `logs/pipeline.log`: sequência operacional e stack trace em falhas;
- `reports/data_quality_report.json`: resultado de cada regra;
- `reports/pipeline_metrics.json`: resumo da execução;
- artefato `pipeline-evidence`: relatórios e logs publicados pela CI.

## Limpeza segura

```bash
python -m src.clean_outputs
```

O comando remove apenas os caminhos conhecidos gerados pelo pipeline. Contratos, código, documentação e arquivos adicionais não são removidos.
