# Storage process

* `main.sh` generates mock data at a given period, calls `push.sh` at a given period
* `push.sh` Syncs files to Azure blob storage (includes lock file to ensure long-running sync process is not restarted.)

## Installation

Follow instructions at https://rclone.org/azureblob/ to create an Azure blob container called `rclone`.

```shell
rclone config
# ... additional config input
```

Run the main script:

```
./main.sh
```

