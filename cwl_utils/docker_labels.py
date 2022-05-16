"""
This script extracts metadata from Docker container labels.
"""

import docker # must be added to requirements.txt?

# Set up a client
client = docker.from_env()

# Use one of the BioContainer images which have labels
# image_name = "bwa:build_0.7.17" # built Dockerfile https://github.com/BioContainers/containers/blob/ba5a83aea2e4c1bf3b25a18b7f49745669a74950/bwa/0.7.17/Dockerfile
image_name = "samtools:build_1.2-0" # built from https://github.com/BioContainers/containers/blob/ba5a83aea2e4c1bf3b25a18b7f49745669a74950/samtools/1.2/Dockerfile

# docker inspect <image_name> --format='{{json .Config.Labels}}'
im = client.images.list(image_name)

for i in im:
    labels = i.labels
    print(labels) # dict of labels
    id = i.id
    print(type(id)) # str: the checksum with sha256: prefix