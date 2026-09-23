# Camadas de dados

- `raw/`: arquivo recebido sem transformações;
- `processed/`: pedidos aprovados e tipados;
- `quarantine/`: registros rejeitados com os motivos.

Os CSVs são gerados por `python -m src.pipeline` e ignorados pelo Git para evitar versionar artefatos reproduzíveis.
