# MikroTik Onboarding for ARGOS

The documents are separated by how often they are used.

| Document | When to use |
|---|---|
| [`01_ONE_TIME_SETUP.md`](./01_ONE_TIME_SETUP.md) | Once, when preparing ARGOS |
| [`02_MIKROTIK_REGISTRATION.md`](./02_MIKROTIK_REGISTRATION.md) | For every new device |
| [`03_BEST_PRACTICES.md`](./03_BEST_PRACTICES.md) | When applying additional security hardening |
| [`04_TROUBLESHOOTING.md`](./04_TROUBLESHOOTING.md) | Only when something fails |

## Standard

```text
CHR:            10.3.3.1
ARGOS server:   10.3.3.254
MikroTik:       10.3.3.X
Network:        10.3.3.0/24
API-SSL:        8729/TCP
User:           argos-api
```

Replace `X` with the number reserved for the MikroTik device.
