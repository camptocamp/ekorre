import os
import argparse
import logging
import time
import boto3
from botocore.exceptions import ClientError
from pytimeparse.timeparse import timeparse
from prometheus_client import start_http_server, Gauge

# Prometheus metrics
metrics_description = {
        'backup_start_time': "Timestamp of when the backup has been started",
        'backup_end_time': "Timestamp of when the backup has ended",
        'backup_success': "Status of the backup",
    }
metrics = {}

def _setup_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(log_level))
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

def _get_ekorre_role():
    iam_client = boto3.client('iam')
    role = iam_client.get_role(RoleName='ekorre')
    return role['Role']['Arn']

def _list_rds_snapshots():
    rds_client = boto3.client('rds')
    snapshots = rds_client.describe_db_snapshots(
                SnapshotType="automated")
    return [s['DBSnapshotIdentifier'].replace('rds:', '') for s in snapshots['DBSnapshots']]

def _list_s3_snapshots(bucket):
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(
                Bucket=bucket,
                Delimiter='/')

    if len(response['CommonPrefixes']) == 0:
        return []

    return [obj['Prefix'].replace('/', '') for obj in response['CommonPrefixes']]

def _list_snapshots_to_backup(rds_snapshots, s3_snapshots):
    return [x for x in rds_snapshots if x not in s3_snapshots]

def _wait_for_export(rds_client, export_id):
    while True:
        res = rds_client.describe_export_tasks(ExportTaskIdentifier=export_id)
        if len(res['ExportTasks']) == 0:
            return

        status = res['ExportTasks'][0]['Status']
        if status not in ('IN_PROGRESS', 'STARTING'):
            logging.info("Export `%s` ended with status: %s", export_id, status)
            if status == "COMPLETE":
                return
            else:
                raise Exception("Export `%s` did not ended successfully: %s".format(export_id, status))
        time.sleep(30)

def _set_metric(metric_name, snapshot_name):
    global metrics
    if metric_name not in metrics:
        metrics[metric_name] = Gauge(
            "ekorre_{}".format(metric_name),
            metrics_description[metric_name],
            ['snapshot'])
    return metrics[metric_name].labels(snapshot=snapshot_name)


def _backup_snapshot(bucket, snapshot_name, ekorre_role, kms_key):
    rds_client = boto3.client('rds')

    db_snapshots = rds_client.describe_db_snapshots(
                DBSnapshotIdentifier="rds:{}".format(snapshot_name))

    if len(db_snapshots['DBSnapshots']) == 0:
        return

    snapshot = db_snapshots['DBSnapshots'][0]

    logging.info("Backing up snapshot `%s`", snapshot_name)
    _set_metric('backup_start_time', snapshot_name).set_to_current_time()
    try:
        response = rds_client.start_export_task(
            ExportTaskIdentifier=snapshot_name,
            SourceArn=snapshot['DBSnapshotArn'],
            S3BucketName=bucket,
            IamRoleArn=ekorre_role,
            KmsKeyId=kms_key,
        )
        export_id = response['ExportTaskIdentifier']
        _wait_for_export(rds_client, export_id)
    except ClientError as err:
        if err.response['Error']['Code'] == "ExportTaskAlreadyExists":
            logging.info("attaching to running export task...")
            _wait_for_export(rds_client, snapshot_name)
        else:
            _set_metric('backup_success', snapshot_name).set(0)
            logging.error("Failed to backup snapshot `%s`: %s", snapshot_name, err)
    except Exception as err:
        _set_metric('backup_success', snapshot_name).set(0)
        logging.error("Failed to backup snapshot `%s`: %s", snapshot_name, err)
    else:
        _set_metric('backup_success', snapshot_name).set(1)
        logging.info("Snapshot `%s` successfully backed up", snapshot_name)
    finally:
        _set_metric('backup_end_time', snapshot_name).set_to_current_time()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", help="Logging level (default: INFO). \
                            (EKORRE_LOG_LEVEL)",
                        type=str, default=os.environ.get(
                            'EKORRE_LOG_LEVEL', 'INFO'))
    parser.add_argument("--address", help="Address the daemon will bind on (default: 0.0.0.0). \
                            (EKORRE_DAEMON_ADDRESS)",
                        type=str, default=os.environ.get(
                            'EKORRE_DAEMON_ADDRESS', '0.0.0.0'))
    parser.add_argument("--port", help="Port the daemon will bind on (default: 8582). \
                            (EKORRE_DAEMON_PORT)",
                        type=str, default=os.environ.get(
                            'EKORRE_DAEMON_PORT', '8582'))
    parser.add_argument("--destination-bucket", help="Bucket where the snapshot will be stored. \
                            (EKORRE_DESTINATION_BUCKET)",
                        type=str, default=os.environ.get(
                            'EKORRE_DESTINATION_BUCKET'))
    parser.add_argument("--kms-key", help="KMS key used to encrypt the backups. \
                            (EKORRE_KMS_KEY)",
                        type=str, default=os.environ.get(
                            'EKORRE_KMS_KEY'))
    parser.add_argument("--refresh-interval",
                        help="Interval between the refresh of the snapshots' list (default: 24h). \
                                (EKORRE_REFRESH_INTERVAL)",
                        type=str, default=os.environ.get(
                            'EKORRE_REFRESH_INTERVAL', '24h'))

    args, unknown = parser.parse_known_args()
    _setup_logging(args.log_level)

    refresh_interval = timeparse(args.refresh_interval)

    start_http_server(int(args.port), addr=args.address)

    ekorre_role = _get_ekorre_role()

    while True:
        try:
            rds_snapshots = _list_rds_snapshots()
            s3_snapshots = _list_s3_snapshots(args.destination_bucket)
            snapshots_to_backup = _list_snapshots_to_backup(rds_snapshots, s3_snapshots)
            for snapshot in snapshots_to_backup:
                _backup_snapshot(args.destination_bucket, snapshot, ekorre_role, args.kms_key)
            time.sleep(refresh_interval)
        except (KeyboardInterrupt, SystemExit):
            raise


if __name__ == '__main__':
    main()
