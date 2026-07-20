# Cadastro de um MikroTik no ARGOS

Repita este procedimento para cada equipamento.

Substitua `X` pelo número reservado.

Exemplo:

```text
X = 250
IP = 10.3.3.250
```

## 1. Reservar e testar o IP

No CHR, o peer deve usar:

```text
allowed-address=10.3.3.X/32
```

No MikroTik, a interface ARGOS deve possuir:

```text
10.3.3.X/24
```

Testes:

```routeros
/ping 10.3.3.1 count=5
```

```powershell
ping 10.3.3.X
```

Só prossiga com handshake e ping funcionando.

## 2. Backup recomendado

```routeros
/system backup save name=pre-argos-10.3.3.X
/export hide-sensitive=yes file=pre-argos-10.3.3.X
```

## 3. Emitir o certificado no CHR

```routeros
/certificate add \
    name=argos-mkt-10.3.3.X-template \
    common-name="argos-mkt-10.3.3.X" \
    organization="BIONIC" \
    subject-alt-name=IP:10.3.3.X \
    key-size=2048 \
    digest-algorithm=sha256 \
    days-valid=730 \
    key-usage=digital-signature,key-encipherment,tls-server

/certificate sign \
    argos-mkt-10.3.3.X-template \
    ca=argos-ca \
    name=argos-mkt-10.3.3.X
```

Confira se o SAN é exatamente:

```text
IP:10.3.3.X
```

## 4. Exportar

```routeros
/certificate export-certificate \
    argos-mkt-10.3.3.X \
    type=pkcs12 \
    export-passphrase="SENHA_TEMPORARIA" \
    file-name=argos-mkt-10.3.3.X
```

Transfira para o MikroTik:

```text
argos-ca.crt
argos-mkt-10.3.3.X.p12
```

## 5. Importar no MikroTik

```routeros
/certificate import \
    file-name=argos-ca.crt \
    name=argos-ca \
    trusted=yes

/certificate import \
    file-name=argos-mkt-10.3.3.X.p12 \
    name=argos-mkt-10.3.3.X \
    passphrase="SENHA_TEMPORARIA" \
    trusted=yes
```

Confira o nome real:

```routeros
/certificate print
```

O certificado do equipamento precisa possuir chave privada.

## 6. Criar usuário do ARGOS

Crie o grupo somente quando ele ainda não existir:

```routeros
/user group add \
    name=argos-monitor \
    policy=read,api
```

Crie o usuário:

```routeros
/user add \
    name=argos-api \
    group=argos-monitor \
    address=10.3.3.254/32 \
    password="SENHA_FORTE_E_EXCLUSIVA"
```

Não use `admin`.

## 7. Configurar a API-SSL

Use o nome exato do certificado importado:

```routeros
/ip service set api-ssl \
    disabled=no \
    port=8729 \
    certificate=argos-mkt-10.3.3.X \
    address=10.3.3.254/32

/ip service set api disabled=yes
```

Confira:

```routeros
/ip service print detail where name~"api"
```

Esperado:

```text
api:      disabled
api-ssl:  enabled
port:     8729
address:  10.3.3.254/32
```

## 8. Liberar no firewall

Adicione somente quando não existir regra equivalente:

```routeros
/ip firewall filter add \
    chain=input \
    action=accept \
    protocol=tcp \
    src-address=10.3.3.254/32 \
    dst-port=8729 \
    in-interface=argos.mkt \
    comment="ARGOS - API-SSL" \
    place-before=0
```

Troque `argos.mkt` pelo nome real da interface.

Não crie NAT.

## 9. Testar

Porta:

```powershell
Test-NetConnection 10.3.3.X -Port 8729
```

TLS, dentro de `backend`:

```powershell
@'
import socket
import ssl

host = "10.3.3.X"
context = ssl.create_default_context(cafile="certs/argos-ca.crt")

with socket.create_connection((host, 8729), timeout=10) as connection:
    with context.wrap_socket(connection, server_hostname=host) as tls:
        print("TLS:", tls.version())
        print("TLS validation: OK")
'@ | python -
```

## 10. Cadastrar no dashboard

```text
Nome: nome do equipamento
Management IP: 10.3.3.X
API Port: 8729
Username: argos-api
Password: senha exclusiva
Public IP: opcional
```

Valide:

```text
Status online
Identity
Modelo
RouterOS
CPU
Memória
Uptime
Último contato
```

## 11. Limpeza

Depois de confirmar o funcionamento, remova o `.p12` dos Files do MikroTik, do CHR e do computador.

```routeros
/file remove "argos-mkt-10.3.3.X.p12"
```

Não remova os certificados instalados.

## Checklist

- [ ] IP reservado
- [ ] WireGuard funcionando
- [ ] Certificado com SAN correto
- [ ] CA e certificado importados
- [ ] Usuário `argos-api`
- [ ] API-SSL em `8729`
- [ ] API comum desabilitada
- [ ] Firewall restrito ao ARGOS
- [ ] TCP e TLS validados
- [ ] Equipamento online no dashboard
- [ ] `.p12` removido
