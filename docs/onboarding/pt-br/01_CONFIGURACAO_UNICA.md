# Configuração única do ARGOS

Execute este documento somente na preparação inicial.

## 1. Padrão da rede

```text
CHR:            10.3.3.1
Servidor ARGOS: 10.3.3.254
Equipamentos:   10.3.3.2 até 10.3.3.253
```

Cada peer do CHR deve possuir um `/32` exclusivo.

## 2. Criar a CA no CHR

Confira a hora:

```routeros
/system clock print
/system ntp client print
```

Crie e assine:

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

Confira:

```routeros
/certificate print detail where name="argos-ca"
```

Essa CA será reutilizada em todos os equipamentos.

## 3. Exportar a CA pública

```routeros
/certificate export-certificate \
    argos-ca \
    type=pem \
    file-name=argos-ca
```

Baixe:

```text
argos-ca.crt
```

A chave privada da CA permanece no CHR.

## 4. Configurar o backend

Copie a CA para:

```text
backend/certs/argos-ca.crt
```

No `backend/.env`:

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

Não troque essa chave depois que existirem senhas cadastradas.

## 5. Backups

No `.gitignore`:

```gitignore
backups/
*.db
*.db-shm
*.db-wal
.env
.env.*
```

Backup:

```powershell
cd backend
New-Item backups -ItemType Directory -Force

Copy-Item .\argos.db `
  ".\backups\argos-$(Get-Date -Format 'yyyyMMdd-HHmmss').db"

Copy-Item .\.env `
  ".\backups\env-$(Get-Date -Format 'yyyyMMdd-HHmmss').backup"
```

Inicie o backend dentro da pasta `backend` e use somente um worker enquanto o polling estiver integrado ao FastAPI.
