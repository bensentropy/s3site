# coding: utf-8
from __future__ import absolute_import, unicode_literals
from functools import partial
import click
import os
import datetime as dt
import SimpleHTTPServer
import SocketServer
from fnmatch import fnmatch
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import yaml
import arrow
from multiprocessing.dummy import Pool as ThreadPool
import hashlib


@click.group()
def cli():
    pass

@cli.command()
@click.option('--port', default=8000, help='port for development server', type=int)
def serve(port):
    """
    Launch a simple development server
    """
    click.echo("development server running at port: {0}".format(port))

    handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", port), handler)
    httpd.serve_forever()


@cli.command()
def modified():
    """
    List local files modified since the last deployment
    """
    click.echo("Listing local modified files")
    [click.echo(x) for x in get_modified_files()]


@cli.command()
def diff_remote():
    """
    List local files not in the remote bucket
    """
    [click.echo(x.name) for x in get_remote_diff()]


@cli.command()
def truncate():
    """
    Remove remote s3 files not in the local directory
    """
    click.echo("Truncating remote s3 bucket")
    for item in get_remote_diff():
        click.echo("{0} deleted".format(item.name))
        item.delete()


@cli.command()
def sync():
    """
    Sync local modified files to remote s3
    """
    click.echo('deploying site to s3')

    bucket = get_bucket()
    modified_files = get_modified_files(bucket)

    pool = ThreadPool(4)
    pool.map(partial(upload_file, bucket), modified_files)

    click.echo('Site deployed')


@cli.command()
def ls():
    """
    List remote files in s3 bucket
    """
    [click.echo(x) for x in get_remote_files().keys()]


def upload_file(bucket, file_name):
    k = Key(bucket)
    k.key = file_name
    k.set_contents_from_filename(file_name)
    k.set_acl('public-read')

    click.echo('Published {0}'.format(file_name))


def get_bucket():
    settings = get_aws_settings()
    conn = S3Connection(aws_access_key_id=settings['access_key_id'],
                        aws_secret_access_key=settings['secret_access_key'],
                        host=settings['endpoint'])

    return conn.get_bucket(settings['bucket'])


def get_remote_diff():
    local_files = get_local_files()
    remote_files = get_remote_files()

    diff_paths = set(remote_files.keys()).difference(set(local_files.keys()))
    return [remote_files[path] for path in diff_paths]


def get_local_files():
    ignore_patterns = get_ignore_patterns()
    all_files = {}

    for root, dirs, files in os.walk('.'):
        for file_name in files:
            path = os.path.join(root, file_name)[2:]
            # ignore excluded patterns
            if any([fnmatch(path, pattern) for pattern in ignore_patterns]):
                continue
            st = os.stat(path)
            mod_time = dt.datetime.fromtimestamp(st.st_mtime)

            all_files[path] = arrow.get(mod_time)

    return all_files


def get_remote_files(bucket=None):
    if not bucket:
        bucket = get_bucket()

    remote_files = {}
    for remote_file in bucket.list():
        file_name = remote_file.name
        # Ignore directories
        if file_name[-1] == "/":
            continue

        remote_files[file_name] = remote_file

    return remote_files


def hash_file(file_name, block_size=65536):
    hash = hashlib.md5()
    with open(file_name, "r+b") as f:
        buf = f.read(block_size)
        while len(buf) > 0:
            hash.update(buf)
            buf = f.read(block_size)
    return hash.hexdigest()


def get_modified_files(bucket=None):
    local_files = get_local_files()
    remote_files = get_remote_files(bucket)

    modified_files = []
    for path, last_modified in local_files.items():
        if path not in remote_files or remote_files[path].etag[1:-1] != hash_file(path):
            modified_files.append(path)

    return modified_files


def get_ignore_patterns():
    ignore_patterns = [".s3siteignore", "s3site.yaml"]

    try:
        with open(".s3siteignore") as f:
            user_patterns = f.read().splitlines()
            ignore_patterns.extend([pattern.strip() for pattern in user_patterns])
    except IOError:
        # user may not have set .s3siteignore
        pass

    return ignore_patterns


def get_aws_settings():
    with open('s3site.yaml') as f:
        settings = yaml.safe_load(f)

    return settings["aws"]
