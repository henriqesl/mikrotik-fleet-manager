# Registering a MikroTik in ARGOS

Repeat this procedure for every device.

Replace `X` with the reserved number.

Example:

```text
X = 250
IP = 10.3.3.250
```

## 1. Reserve and test the IP address

On the CHR, the peer must use:

```text
allowed-address=10.3.3.X/32
```

On the MikroTik, the ARGOS interface must have:

```text
10.3.3.X/24
```

Tests:

```routeros
/ping 10.3.3.1 count=5
```

```powershell
ping 10.3.3.X
```

Continue only after the handshake and ping are working.

## 2. Recommended backup

```routeros
/system backup save name=pre-argos-10.3.3.X
/export hide-sensitive=yes file=pre-argos-10.3.3.X
```

## 3. Issue the certificate on the CHR

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

Verify that the SAN is exactly:

```text
IP:10.3.3.X
```

## 4. Export the certificate

```routeros
/certificate export-certificate \
    argos-mkt-10.3.3.X \
    type=pkcs12 \
    export-passphrase="TEMPORARY_PASSWORD" \
    file-name=argos-mkt-10.3.3.X
```

Transfer these files to the MikroTik:

```text
argos-ca.crt
argos-mkt-10.3.3.X.p12
```

## 5. Import the certificates on the MikroTik

```routeros
/certificate import \
    file-name=argos-ca.crt \
    name=argos-ca \
    trusted=yes

/certificate import \
    file-name=argos-mkt-10.3.3.X.p12 \
    name=argos-mkt-10.3.3.X \
    passphrase="TEMPORARY_PASSWORD" \
    trusted=yes
```

Check the actual imported name:

```routeros
/certificate print
```

The device certificate must include its private key.

## 6. Create the ARGOS user

Create the group only if it does not already exist:

```routeros
/user group add \
    name=argos-monitor \
    policy=read,api
```

Create the user:

```routeros
/user add \
    name=argos-api \
    group=argos-monitor \
    address=10.3.3.254/32 \
    password="STRONG_UNIQUE_PASSWORD"
```

Do not use `admin`.

## 7. Configure API-SSL

Use the exact name of the imported certificate:

```routeros
/ip service set api-ssl \
    disabled=no \
    port=8729 \
    certificate=argos-mkt-10.3.3.X \
    address=10.3.3.254/32

/ip service set api disabled=yes
```

Verify:

```routeros
/ip service print detail where name~"api"
```

Expected:

```text
api:      disabled
api-ssl:  enabled
port:     8729
address:  10.3.3.254/32
```

## 8. Allow access through the firewall

Add this rule only when no equivalent rule already exists:

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

Replace `argos.mkt` with the actual interface name.

Do not create NAT for this connection.

## 9. Test the connection

Port test:

```powershell
Test-NetConnection 10.3.3.X -Port 8729
```

TLS test from the `backend` directory:

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

## 10. Register the device in the dashboard

```text
Name: device name
Management IP: 10.3.3.X
API Port: 8729
Username: argos-api
Password: device-specific password
Public IP: optional
```

Validate:

```text
Online status
Identity
Model
RouterOS
CPU
Memory
Uptime
Last contact
```

## 11. Cleanup

After confirming that everything works, remove the `.p12` file from the MikroTik, the CHR, and the computer.

```routeros
/file remove "argos-mkt-10.3.3.X.p12"
```

Do not remove the installed certificates.

## Checklist

- [ ] IP address reserved
- [ ] WireGuard working
- [ ] Certificate has the correct SAN
- [ ] CA and device certificate imported
- [ ] `argos-api` user created
- [ ] API-SSL running on `8729`
- [ ] Unencrypted API disabled
- [ ] Firewall restricted to ARGOS
- [ ] TCP and TLS validated
- [ ] Device online in the dashboard
- [ ] `.p12` file removed
