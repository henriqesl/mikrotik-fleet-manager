# Boas práticas

Aplique conforme o ambiente. Não desabilite serviços necessários para a operação.

## Serviços

Recomendado:

```routeros
/ip service disable telnet
/ip service disable ftp
/ip service disable www
/ip service disable api
```

Quando não forem utilizados:

```routeros
/ip service disable ssh
/ip service disable www-ssl
```

Restrinja o WinBox às redes administrativas:

```routeros
/ip service set winbox \
    address=10.3.3.254/32,<REDE_LOCAL_ADMIN>
```

Teste o acesso antes de encerrar a sessão.

## Usuário

O grupo do ARGOS deve começar somente com:

```text
read,api
```

Não conceda `full`, `write`, `policy` ou `sensitive` sem necessidade comprovada.

Use uma senha diferente em cada equipamento.

## Serviços auxiliares

Quando não forem necessários:

```routeros
/tool bandwidth-server set enabled=no
/ip proxy set enabled=no
/ip socks set enabled=no
/ip upnp set enabled=no
```

Quando o MikroTik não atuar como DNS:

```routeros
/ip dns set allow-remote-requests=no
```

## Acesso por MAC

Aplique somente quando a operação não depender dele:

```routeros
/tool mac-server set allowed-interface-list=none
/tool mac-server mac-winbox set allowed-interface-list=none
/tool mac-server ping set enabled=no
```

## Certificados e segredos

Nunca envie ao Git:

```text
.p12
chave privada da CA
.env
banco real
senhas
```

Registre a data de expiração e o fingerprint de cada certificado.

Faça backup do banco e da chave Fernet em conjunto.
