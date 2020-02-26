import unittest
import boto3
from moto import mock_rds, mock_s3
from mock import patch, mock
from botocore.stub import Stubber

from ekorre import core

class TestsEkorre(unittest.TestCase):

    def test_list_rds_snapshots(self):
        fakeSnapshots = {
                'DBSnapshots': [
                    {
                        'DBSnapshotIdentifier': 'rds:foo',
                    },
                    {
                        'DBSnapshotIdentifier': 'rds:bar',
                    }
                ]
            }
        with patch('ekorre.core.boto3.client') as mock:
            instance = mock.return_value
            instance.describe_db_snapshots.return_value = fakeSnapshots

            snapshots = core._list_rds_snapshots()
            self.assertEqual(["foo","bar"], snapshots)

    @mock_s3
    def test_list_s3_snapshots(self):
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket='toto')
        cl = boto3.client('s3')
        cl.put_object(Bucket='toto', Key='foo/lorem', Body='blabla')
        cl.put_object(Bucket='toto', Key='bar/ipsum/set', Body='blabla')

        snapshots = core._list_s3_snapshots('toto')
        self.assertListEqual(sorted(["foo","bar"]), sorted(snapshots))

    def test_list_snapshots_to_backup(self):
        s3_snapshots = ["lorem", "ipsum", "dolor"]
        rds_snapshots = ["dolor", "sit", "amet"]

        expected_result = ["sit", "amet"]

        result = core._list_snapshots_to_backup(rds_snapshots, s3_snapshots)

        self.assertEqual(expected_result, result)
