import logging
import os
import sys
import json
import warnings
from unittest import TestCase
from unittest.mock import patch


class Tests(TestCase):

    def setUp(self) -> None:
        # False Alarm of ResourceWarning. Boto3 doesnt hold long living socket connections. Unittest falsely thinks so.
        logger = logging.getLogger()
        logger.level = logging.DEBUG
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)-10s] (%(name)s): %(message)s"))
        logger.addHandler(stream_handler)

        log_handler = logging.getLogger('botocore')
        log_handler.setLevel('WARNING')
        log_handler = logging.getLogger('boto3')
        log_handler.setLevel('WARNING')
        log_handler = logging.getLogger('kmhelper')
        log_handler.setLevel('WARNING')
        log_handler = logging.getLogger('urllib3')
        log_handler.setLevel('WARNING')
        log_handler = logging.getLogger('s3transfer')
        log_handler.setLevel('WARNING')
        warnings.simplefilter("ignore", ResourceWarning)

    @patch("boto3.client")
    def test_main(self, boto3_client_mock):
        bucket = "test-bucket"
        os.environ['BADGE_UPLOADER_BUCKET'] = bucket
        from badge_uploader_stack.badge_uploader_lambda import handler

        event = {
            "body": json.dumps({
                "total_coverage": 1,
                "branch": "branch",
                "project": "project"
            })
        }

        self.assertEqual(
            {'statusCode': 200, 'headers': {'Content-Type': 'application/json'},
             'body': '{"url": "https://s3.amazonaws.com/test-bucket/215fbc5fdf64b4f4324326534bba1faea1b12bfe2aaf530390ba79442b5e36a5.svg"}'},
            handler.main(event=event, context=None)
        )