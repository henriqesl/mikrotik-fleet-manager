# Diagnóstico rápido

## Ping não funciona

Confira:

```text
Handshake
Allowed Address
IP 10.3.3.X
Rotas
Firewall
```

```routeros
/interface wireguard peers print detail
/ip address print
/ip route print
```

## Porta 8729 não responde

```powershell
Test-NetConnection 10.3.3.X -Port 8729
```

```routeros
/ip service print detail where name="api-ssl"
/ip firewall filter print stats
```

Confira se a API-SSL está habilitada, na porta 8729 e permitindo `10.3.3.254/32`.

## TCP funciona, mas TLS falha

Confira:

```text
CA usada pelo backend
SAN do certificado
Data e hora
Certificado selecionado na API-SSL
Reinício do backend
```

```routeros
/certificate print detail where name~"argos"
/ip service print detail where name="api-ssl"
/system clock print
```

Erro de incompatibilidade de IP exige um novo certificado com:

```text
subject-alt-name=IP:10.3.3.X
```

Não desabilite a validação TLS.

## Falha de login

```routeros
/user print detail where name="argos-api"
/user group print detail where name="argos-monitor"
/log print where message~"login|auth|api"
```

O grupo deve possuir `read,api` e o usuário deve permitir `10.3.3.254/32`.

## Dashboard mostra `error`

Confira:

```text
Mensagem do drawer
Logs do backend
Status do polling
Caminho da CA
Diretório de execução
```

Inicie dentro de:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

## Banco inesperadamente vazio

Procure outros arquivos:

```powershell
Get-ChildItem -Path .. -Filter *.db -Recurse
```

Isso pode acontecer quando o backend é iniciado fora da pasta `backend`.
