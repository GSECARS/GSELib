# Cloud

The `cloud` module provides storage and share management for cloud services. Currently supported: **Nextcloud**.

## Installation

```bash
pip install 'gselib[cloud]'
```

## Nextcloud CLI

All commands are available under `gselib cloud nextcloud`. Storage commands (create, list, delete) run `occ` on the server; share commands use the Nextcloud REST API.

### Configuration

**Storage management** runs `occ` locally or over SSH. Configure via flags or environment variables:

| Flag | Environment variable | Description |
|---|---|---|
| `--occ-cmd` | `NEXTCLOUD_OCC_CMD` | Full `occ` invocation (required) |
| `--ssh-host` | `NEXTCLOUD_SSH_HOST` | SSH host (omit to run locally) |
| `--ssh-user` | `NEXTCLOUD_SSH_USER` | SSH username |
| `--ssh-key` | `NEXTCLOUD_SSH_KEY` | Path to private key (prompts for password if omitted) |

**Share management** uses the OCS REST API. Configure via flags or environment variables:

| Flag | Environment variable | Description |
|---|---|---|
| `--url` | `NEXTCLOUD_URL` | Nextcloud base URL |
| `--user` | `NEXTCLOUD_USER` | Admin username |
| `--password` | `NEXTCLOUD_PASSWORD` | Admin password (prompted if omitted) |

### External storage

Local (no SSH):

```bash
gselib cloud nextcloud --occ-cmd "php occ" create-storage --mount MyData --path /srv/data
```

Via SSH with key:

```bash
gselib cloud nextcloud \
    --occ-cmd "php occ" \
    --ssh-host myserver --ssh-user admin --ssh-key ~/.ssh/id_ed25519 \
    create-storage --mount MyData --path /srv/data
```

Nextcloud AIO (Docker over SSH):

```bash
gselib cloud nextcloud \
    --occ-cmd "docker exec --user www-data nextcloud-aio-nextcloud php occ" \
    --ssh-host myserver --ssh-user admin --ssh-key ~/.ssh/id_ed25519 \
    create-storage --mount MyData --path /srv/data --users alice bob
```

With groups:

```bash
gselib cloud nextcloud --occ-cmd "php occ" \
    create-storage --mount Shared --path /srv/shared --groups scientists
```

List storages:

```bash
gselib cloud nextcloud --occ-cmd "php occ" list-storages
```

Delete a storage:

```bash
gselib cloud nextcloud --occ-cmd "php occ" delete-storage --id 3
```

### Shares

Share a path:

```bash
gselib cloud nextcloud \
    --url https://nextcloud.example.org --user admin \
    share --nc-path /MyData --recipients alice bob@external.org \
    --permissions read update
```

Available permissions: `read`, `update`, `create`, `delete`, `share`, `all`.

List shares:

```bash
gselib cloud nextcloud --url https://nextcloud.example.org --user admin \
    list-shares --nc-path /MyData
```

Delete a share:

```bash
gselib cloud nextcloud --url https://nextcloud.example.org --user admin \
    delete-share --id 7
```

## Nextcloud library

```python
from gselib.cloud import NextcloudClient, NextcloudOCC

# External storage via occ (local)
with NextcloudOCC(occ_cmd="php occ") as occ:
    mount = occ.create_local_storage("MyData", "/srv/data", applicable_users=["alice"])
    print(mount["id"])
    mounts = occ.list_storages()
    occ.delete_storage(mount["id"])

# External storage via SSH
with NextcloudOCC(host="myserver", user="admin", key_path="~/.ssh/id_ed25519", occ_cmd="php occ") as occ:
    occ.create_local_storage("MyData", "/srv/data")

# Nextcloud AIO (Docker over SSH)
with NextcloudOCC(
    host="myserver",
    user="admin",
    key_path="~/.ssh/id_ed25519",
    occ_cmd="docker exec --user www-data nextcloud-aio-nextcloud php occ",
) as occ:
    occ.create_local_storage("MyData", "/srv/data")

# Shares via REST API
client = NextcloudClient("https://nextcloud.example.org", "admin", "password")
client.share_with_many("/MyData", ["alice", "bob@external.org"], permissions=NextcloudClient.perm_read)
shares = client.list_shares(path="/MyData")
client.delete_share(shares[0]["id"])
```
