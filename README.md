# Ekorre

## Usage

```
usage: ekorre [-h] [--log-level LOG_LEVEL] [--address ADDRESS] [--port PORT]
              [--destination-bucket DESTINATION_BUCKET] [--kms-key KMS_KEY]
              [--refresh-interval REFRESH_INTERVAL]

optional arguments:
  -h, --help            show this help message and exit
  --log-level LOG_LEVEL
                        Logging level
  --address ADDRESS     Address the daemon will bind on.
  --port PORT           Port the daemon will bind on.
  --destination-bucket DESTINATION_BUCKET
                        Bucket where the snapshot will be stored.
  --kms-key KMS_KEY     KMS key used to encrypt the backups.
  --refresh-interval REFRESH_INTERVAL
                        Interval between the refresh of the snapshots' list.
```
