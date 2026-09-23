# Contrato de dados

O contrato canônico está em `contracts/sales_orders.yml` e possui versão independente. A versão atual é `1.0`.

## Campos

| Campo | Tipo processado | Obrigatório | Regra semântica |
|---|---|---:|---|
| `order_id` | string | sim | identificador único do pedido |
| `order_date` | datetime | sim | data válida do pedido |
| `customer_id` | string | sim | identificador do cliente |
| `product_id` | string | sim | identificador do produto |
| `product_name` | string | sim | nome de exibição do produto |
| `category` | string | sim | valor pertencente ao domínio de categorias |
| `quantity` | int64 | sim | inteiro entre 1 e 100 |
| `unit_price` | float64 | sim | valor maior que zero |
| `discount_pct` | float64 | sim | proporção entre 0 e 0,5 |
| `payment_method` | string | sim | valor pertencente ao domínio de pagamentos |
| `delivery_status` | string | sim | valor pertencente ao domínio de entrega |
| `country` | string | sim | valor pertencente ao domínio de países |
| `total_amount` | float64 | sim | quantidade × preço × (1 − desconto) |

## Domínios

- categorias: `Electronics`, `Home`, `Sports`, `Books`, `Beauty`;
- pagamentos: `Card`, `Pix`, `Boleto`, `Wallet`;
- entrega: `Delivered`, `Shipped`, `Processing`, `Cancelled`;
- países: `Brazil`, `Argentina`, `Chile`, `Colombia`.

## Evolução do contrato

Mudanças compatíveis, como adicionar um valor de domínio, incrementam a versão secundária. Remover/renomear uma coluna ou mudar sua semântica exige uma nova versão principal e migração dos consumidores.

## Entrada própria

O modo `--skip-generate` aceita `data/raw/sales_orders_raw.csv`. O arquivo deve conter exatamente as colunas obrigatórias; valores inválidos dentro dessas colunas são direcionados à quarentena.
