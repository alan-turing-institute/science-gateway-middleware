# Storage process

* `main.sh` generates mock data at a given period, calls `push.sh` at a given period
* `push.sh` Syncs files to Azure blob storage (includes lock file to ensure long-running sync process is not restarted.)