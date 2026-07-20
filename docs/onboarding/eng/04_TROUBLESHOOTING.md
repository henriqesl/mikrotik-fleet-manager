# Quick troubleshooting

## Ping does not work

Check:

```text
Handshake
Allowed Address
10.3.3.X IP address
Routes
Firewall
```

```routeros
/interface wireguard peers print detail
/ip address print
/ip route print
```

## Port 8729 does not respond

```powershell
Test-NetConnection 10.3.3.X -Port 8729
```

```routeros
/ip service print detail where name="api-ssl"
/ip firewall filter print stats
```

Verify that API-SSL is enabled, using port 8729, and allowing `10.3.3.254/32`.

## TCP works, but TLS fails

Check:

```text
CA used by the backend
Certificate SAN
Date and time
Certificate selected for API-SSL
Backend restart
```

```routeros
/certificate print detail where name~"argos"
/ip service print detail where name="api-ssl"
/system clock print
```

An IP mismatch requires a new certificate with:

```text
subject-alt-name=IP:10.3.3.X
```

Do not disable TLS verification.

## Login failure

```routeros
/user print detail where name="argos-api"
/user group print detail where name="argos-monitor"
/log print where message~"login|auth|api"
```

The group must have `read,api`, and the user must allow `10.3.3.254/32`.

## Dashboard shows `error`

Check:

```text
Drawer error message
Backend logs
Polling status
CA path
Working directory
```

Start the backend from:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

## Database is unexpectedly empty

Search for other database files:

```powershell
Get-ChildItem -Path .. -Filter *.db -Recurse
```

This may happen when the backend is started outside the `backend` directory.
