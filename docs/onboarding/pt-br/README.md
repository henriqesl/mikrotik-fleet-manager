# Onboarding de MikroTiks no ARGOS

Os documentos foram separados pela frequência de uso.

| Documento | Quando usar |
|---|---|
| [`01_CONFIGURACAO_UNICA.md`](./01_CONFIGURACAO_UNICA.md) | Uma vez, ao preparar o ARGOS |
| [`02_CADASTRO_DE_MIKROTIK.md`](./02_CADASTRO_DE_MIKROTIK.md) | Para cada equipamento novo |
| [`03_BOAS_PRATICAS.md`](./03_BOAS_PRATICAS.md) | Quando quiser endurecer a segurança |
| [`04_DIAGNOSTICO.md`](./04_DIAGNOSTICO.md) | Somente quando algo falhar |

## Padrão

```text
CHR:            10.3.3.1
Servidor ARGOS: 10.3.3.254
MikroTik:       10.3.3.X
Rede:           10.3.3.0/24
API-SSL:        8729/TCP
Usuário:        argos-api
```

Substitua `X` pelo número reservado para o MikroTik.
