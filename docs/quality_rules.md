# Catálogo de regras de qualidade

## Regras executáveis

| Nome técnico | Dimensão | Critério | Falhas controladas |
|---|---|---|---:|
| `required_columns_present` | Schema | todas as 13 colunas existem | 0 |
| `order_id_not_null` | Completude | identificador não nulo | 5 |
| `order_id_unique` | Unicidade | somente a primeira ocorrência é aceita | 5 |
| `customer_id_not_null` | Completude | cliente não nulo | 5 |
| `order_date_valid` | Validade | conversão para datetime bem-sucedida | 5 |
| `quantity_positive` | Validade | quantidade ≥ 1 | 5 |
| `quantity_within_limit` | Validade | quantidade ≤ 100 | 5 |
| `unit_price_positive` | Validade | preço numérico e > 0 | 5 |
| `discount_valid_range` | Validade | desconto entre 0 e 0,5 | 5 |
| `delivery_status_domain` | Validade | status no domínio do contrato | 5 |
| `category_domain` | Validade | categoria no domínio do contrato | 5 |
| `total_amount_consistent` | Consistência | diferença absoluta máxima de 0,02 | 25 |

O total de falhas por regra é maior que 55 porque algumas anomalias também tornam o total inconsistente. A quantidade de linhas únicas em quarentena permanece 55.

## Dimensões

- **Schema:** estrutura mínima exigida para iniciar o processamento.
- **Completude:** presença de identificadores essenciais.
- **Unicidade:** ausência de duplicação na chave primária.
- **Validade:** tipo, intervalo e domínio permitidos.
- **Consistência:** coerência entre campos relacionados.

## Pontuação

Para cada regra, a pontuação é calculada como:

`100 × (1 − registros_com_falha / registros_brutos)`

A pontuação de uma dimensão é a média das regras pertencentes a ela. As pontuações do raw são informativas; a decisão final usa o quality gate da camada processada.
