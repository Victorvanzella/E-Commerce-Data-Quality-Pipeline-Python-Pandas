# Arquitetura e decisões técnicas

## Objetivo

O pipeline recebe pedidos em lote, verifica o contrato estrutural, mede qualidade registro a registro e entrega somente dados confiáveis para análises. Os registros rejeitados não são apagados: permanecem disponíveis com as causas da rejeição.

## Fluxo

1. **Generate** cria pedidos sintéticos reproduzíveis e injeta anomalias conhecidas.
2. **Extract** lê todas as colunas inicialmente como texto e verifica o contrato mínimo.
3. **Prepare** normaliza textos e converte datas e números sem ocultar erros de conversão.
4. **Evaluate** executa 12 regras vetorizadas e registra todas as falhas de cada linha.
5. **Route** separa registros aprovados e rejeitados.
6. **Validate** aplica um schema Pandera estrito à camada processada.
7. **Publish** grava cinco visões analíticas, um relatório de qualidade e métricas.
8. **Gate** encerra com erro quando o schema, as regras finais ou a taxa mínima falham.

## Camadas

| Camada | Responsabilidade | Mutabilidade |
|---|---|---|
| Raw | preservar a entrada recebida | recriada a cada execução sintética |
| Processed | disponibilizar pedidos válidos e tipados | recriada após validação |
| Quarantine | preservar registros inválidos e motivos | recriada após validação |
| Reports | fornecer indicadores técnicos e de negócio | recriada após publicação |

## Decisões relevantes

### Quarentena em vez de correção automática

Campos críticos como cliente, preço e data não são inferidos. Uma correção automática sem fonte confiável produziria dados aparentemente válidos, mas semanticamente falsos. A quarentena mantém a linha original e acrescenta `rejection_reason`.

### Múltiplas causas por registro

Uma linha pode violar mais de uma regra. Os motivos são separados por `;`, permitindo medir cada regra sem perder a visão do total de registros rejeitados.

### Contrato externo ao código

Domínios e limites estão em YAML. Isso torna as expectativas visíveis, versionáveis e revisáveis sem procurar constantes espalhadas pela implementação.

### Validação em duas etapas

O motor de regras decide roteamento e produz métricas detalhadas. O Pandera atua como barreira final tipada e estrita. As duas camadas têm propósitos complementares.

### Escrita de JSON atômica

Relatórios JSON são escritos em um arquivo temporário e movidos para o destino. Isso reduz o risco de consumidores lerem um documento parcialmente gravado.

### Reprodutibilidade

A fonte utiliza `numpy.random.Generator` com seed. A mesma configuração produz os mesmos pedidos e as mesmas 55 anomalias.

## Quality gate

O status é `PASSED` somente quando:

- todas as 12 regras passam no dataset processado; e
- a taxa de aceitação é igual ou superior a `QUALITY_MIN_ACCEPTANCE_RATE`.

O padrão é 99%. Na execução de referência, 10.000 de 10.055 registros são aceitos, resultando em 99,4530%.

## Idempotência

Com a mesma quantidade de linhas e a mesma seed, as camadas e relatórios CSV são determinísticos. Identificadores de execução e timestamps mudam propositalmente para preservar observabilidade.
