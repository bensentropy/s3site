# S3site

A command line tool to help manage static sites on Amazon's S3 service.


## Usage:

<pre>
  $ pip install s3site
  $ s3site --help
</pre>

Create a s3site.yaml file with your aws settings:

<pre>
aws:
  bucket: "your-bucket-name"
  access_key_id: "your-access-key-id"
  secret_access_key: "your-secret-access-key"
  endpoint: "s3-ap-southeast-1.amazonaws.com"
</pre>  
  
For endpoints see:
https://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region

Optionally create a .s3siteignore file to prevent files being uploaded from your local file system:

<pre>
.git/*
.DS_Store
.gitignore
</pre> 

.s3siteignore uses the fnmatch function see:
https://docs.python.org/2/library/fnmatch.html

Then run the sync command to publish all files in the local directory to s3 bucket
(note files are published with alc set to "public-read"):

<pre>
s3site sync
</pre>

## Road map

* handle large files

## License

Copyright © 2015 Ben Olsen Distributed under the GNU General Public License v3.0.
