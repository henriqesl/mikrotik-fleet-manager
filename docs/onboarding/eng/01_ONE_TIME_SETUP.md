# One-time ARGOS setup

Run this document only during the initial infrastructure setup.

## 1. Network standard

```text
CHR:            10.3.3.1
ARGOS server:   10.3.3.254
Devices:        10.3.3.2 through 10.3.3.253
```

Each CHR peer must have a unique `/32`.

## 2. Create the CA on the CHR

Check the clock:

```routeros
/system clock print
/system ntp client print
```

Create and sign the CA:

```routeros
/certificate add \
    name=argos-ca \
    common-name="ARGOS Root CA" \
    organization="BIONIC" \
    key-size=2048 \
    digest-algorithm=sha256 \
    days-valid=3650 \
    key-usage=key-cert-sign,crl-sign

/certificate sign argos-ca
/certificate set [find where name="argos-ca"] trusted=yes
```

Verify it:

```routeros
/certificate print detail where name="argos-ca"
```

This CA will be reused for every device.

## 3. Export the public CA

```routeros
/certificate export-certificate \
    argos-ca \
    type=pem \
    file-name=argos-ca
```

Download:

```text
argos-ca.crt
```

The CA private key must remain on the CHR.

## 4. Configure the backend

Copy the CA to:

```text
backend/certs/argos-ca.crt
```

In `backend/.env`:

```env
MANAGEMENT_NETWORKS=10.3.3.0/24
ALLOWED_ROUTER_API_PORTS=8729
ROUTEROS_CA_FILE=certs/argos-ca.crt
POLLING_ENABLED=true
```

Preserve:

```env
CREDENTIAL_ENCRYPTION_KEY=...
```

Do not replace this key after credentials have been stored.

## 5. Backups

In `.gitignore`:

```gitignore
backups/
*.db
*.db-shm
*.db-wal
.env
.env.*
```

Create backups:

```powershell
cd backend
New-Item backups -ItemType Directory -Force

Copy-Item .\argos.db `
  ".\backups\argos-$(Get-Date -Format 'yyyyMMdd-HHmmss').db"

Copy-Item .\.env `
  ".\backups\env-$(Get-Date -Format 'yyyyMMdd-HHmmss').backup"
```

Start the backend from the `backend` directory and use only one worker while polling remains integrated into FastAPI.
