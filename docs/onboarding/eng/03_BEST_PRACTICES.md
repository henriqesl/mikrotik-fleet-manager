# Best practices

Apply these recommendations according to the environment. Do not disable services required for operations.

## Services

Recommended:

```routeros
/ip service disable telnet
/ip service disable ftp
/ip service disable www
/ip service disable api
```

When they are not used:

```routeros
/ip service disable ssh
/ip service disable www-ssl
```

Restrict WinBox to administrative networks:

```routeros
/ip service set winbox \
    address=10.3.3.254/32,<LOCAL_ADMIN_NETWORK>
```

Test access before closing the current session.

## User permissions

The ARGOS group should start with only:

```text
read,api
```

Do not grant `full`, `write`, `policy`, or `sensitive` without a confirmed requirement.

Use a different password for every device.

## Auxiliary services

When they are not required:

```routeros
/tool bandwidth-server set enabled=no
/ip proxy set enabled=no
/ip socks set enabled=no
/ip upnp set enabled=no
```

When the MikroTik does not act as the network DNS server:

```routeros
/ip dns set allow-remote-requests=no
```

## MAC access

Apply only when operations do not depend on these features:

```routeros
/tool mac-server set allowed-interface-list=none
/tool mac-server mac-winbox set allowed-interface-list=none
/tool mac-server ping set enabled=no
```

## Certificates and secrets

Never commit:

```text
.p12 files
CA private key
.env
production database
passwords
```

Record each certificate's expiration date and fingerprint.

Back up the database and Fernet key together.
