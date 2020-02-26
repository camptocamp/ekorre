# Ekorre

## Usage

```
usage: ekorre [-h] [--log-level LOG_LEVEL] [--address ADDRESS] [--port PORT]
              [--destination-bucket DESTINATION_BUCKET] [--kms-key KMS_KEY]
              [--refresh-interval REFRESH_INTERVAL]

optional arguments:
  -h, --help            show this help message and exit
  --log-level LOG_LEVEL
                        Logging level (default: INFO). (EKORRE_LOG_LEVEL)
  --address ADDRESS     Address the daemon will bind on (default: 0.0.0.0).
                        (EKORRE_DAEMON_ADDRESS)
  --port PORT           Port the daemon will bind on (default: 8582).
                        (EKORRE_DAEMON_PORT)
  --destination-bucket DESTINATION_BUCKET
                        Bucket where the snapshot will be stored.
                        (EKORRE_DESTINATION_BUCKET)
  --kms-key KMS_KEY     KMS key used to encrypt the backups. (EKORRE_KMS_KEY)
  --refresh-interval REFRESH_INTERVAL
                        Interval between the refresh of the snapshots' list
                        (default: 24h). (EKORRE_REFRESH_INTERVAL)
```
