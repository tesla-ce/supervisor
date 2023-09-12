
# vault write permission error:

failed to initialize barrier: failed to persist keyring: mkdir /vault_data/core: permission denied, on put http://localhost:8200/v1/sys/init

```bash
chmod -R 777 vault
```
