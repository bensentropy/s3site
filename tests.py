# coding: utf-8
from __future__ import absolute_import, unicode_literals
import arrow
import s3site
import mock
import unittest
from click.testing import CliRunner


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.mock_aws_key = mock.MagicMock()
        self.mock_aws_key.name = "home.html"

    @mock.patch('s3site.SocketServer',)
    @mock.patch('s3site.SimpleHTTPServer')
    def test_serve(self, mock_http_server, mock_socket_server):
        runner = CliRunner()
        result = runner.invoke(s3site.serve)
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(mock_http_server.called)
        self.assertTrue(mock_socket_server.TCPServer().serve_forever.called)
        self.assertEqual(result.output, u'development server running at port: 8000\n')

    @mock.patch('s3site.get_modified_files', return_value=["index.html", ], autospec=True)
    def test_modified(self, get_modified_files):
        runner = CliRunner()
        result = runner.invoke(s3site.modified)
        self.assertTrue(get_modified_files.called)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, u'Listing local modified files\nindex.html\n')

    @mock.patch('s3site.get_remote_diff', autospec=True)
    def test_diff_remote(self, get_remote_diff):
        get_remote_diff.return_value = [self.mock_aws_key, ]
        runner = CliRunner()
        result = runner.invoke(s3site.diff_remote)
        self.assertTrue(get_remote_diff.called)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, u'home.html\n')

    @mock.patch('s3site.upload_file', autospec=True)
    @mock.patch('s3site.get_modified_files', autospec=True)
    @mock.patch('s3site.get_bucket', autospec=True)
    def test_sync(self, mock_get_bucket, mock_get_modified_files, mock_upload_file):
        mock_get_modified_files.return_value = [self.mock_aws_key, ]
        runner = CliRunner()
        result = runner.invoke(s3site.sync)

        self.assertTrue(mock_get_bucket.called)
        self.assertTrue(mock_get_modified_files.called)
        self.assertTrue(mock_upload_file.called)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, u'deploying site to s3\nSite deployed\n')

    @mock.patch('s3site.get_remote_files', return_value={"about.html": ""}, autospec=True)
    def test_ls(self, mock_get_remote_files):
        runner = CliRunner()
        result = runner.invoke(s3site.ls)
        self.assertTrue(mock_get_remote_files.called)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, u'about.html\n')

class TestInteractions(unittest.TestCase):
    def setUp(self):
        self.aws_key = mock.MagicMock()
        self.aws_key.name = "home.html"
        self.aws_key.last_modified = "2015-07-13T11:05:23.000Z"

        aws_key_2 = mock.MagicMock()
        aws_key_2.name = "css/"
        self.bucket = mock.MagicMock()
        self.bucket.list.return_value = [self.aws_key, aws_key_2]

    @mock.patch('s3site.click.echo', autospec=True)
    @mock.patch('s3site.Key', return_value=mock.MagicMock())
    def test_upload_file(self, mock_key, mock_echo):
        s3site.upload_file(mock.MagicMock, 'home.html')

        self.assertEqual(mock_key.return_value.key, 'home.html')
        self.assertTrue(mock_key.called)
        self.assertTrue(mock_key.return_value.set_acl.called)
        self.assertTrue(mock_key.return_value.set_contents_from_filename.called)
        self.assertEqual(mock_echo.mock_calls[0][1][0], "Published home.html")

    @mock.patch('s3site.S3Connection')
    @mock.patch('s3site.get_aws_settings', return_value={"access_key_id": "access",
                                                         "secret_access_key": "secret",
                                                         "bucket": "my_bucket",
                                                         "endpoint": "s3-us-west-2.amazonaws.com"})
    def test_get_bucket(self, mock_get_settings, mock_connection):
        s3site.get_bucket()
        self.assertTrue(mock_get_settings.called)
        self.assertTrue(mock_connection.called)

    @mock.patch('s3site.get_remote_files', return_value={"remote.html": "file1"})
    @mock.patch('s3site.get_local_files', return_value={"local.html": "file1"})
    def test_get_remote_diff(self, mock_get_remote_files, mock_get_local_files):
        # mock_get_remote_files.
        results = s3site.get_remote_diff()

        self.assertTrue(mock_get_remote_files.called)
        self.assertTrue(mock_get_local_files.called)
        self.assertEqual(results, [u'file1'])

    def test_get_remote_files(self):
        remote_files = s3site.get_remote_files(self.bucket)

        self.assertEqual(remote_files.keys(), ['home.html'])

    @mock.patch('s3site.get_remote_files')
    @mock.patch('s3site.get_local_files', return_value={"local.html": arrow.get('2013-05-11T21:23:58')})
    def test_get_modified_files(self, mock_get_remote_files, mock_get_local_files):
        mock_get_remote_files.return_value = {"home.html": self.aws_key, }
        result = s3site.get_modified_files()
        self.assertTrue(mock_get_remote_files.called)
        self.assertTrue(mock_get_local_files.called)
        self.assertEqual(result, [u'home.html'])

    def test_get_ignore_patterns(self):
        result = s3site.get_ignore_patterns()
        self.assertEqual(result, [".s3siteignore", "s3site.yaml"])


if __name__ == '__main__':
    unittest.main()
