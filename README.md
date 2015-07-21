# S3site

A command line tool to hlp manage static sites on Amazon's S3 service.


## Usage:

<pre>
  $ pip install git+git://github.com/bensentropy/s3site
  $ s3site --help
</pre>

Create a s3site.yaml file with your aws settings:

<pre>  
aws:
  bucket: "your-bucket-name"
  access_key_id: "your-access-key-id"
  secret_access_key: "your-secret-access-key"
</pre>  
  

Optionally create a .s3siteignore file to prevent files being uploaded from your local file system:

<pre>
.git/*
.DS_Store
.gitignore
</pre> 

.s3siteignore uses the fnmatch function see:
https://docs.python.org/2/library/fnmatch.html

Then run the sync command:

<pre>
s3site sync
</pre>