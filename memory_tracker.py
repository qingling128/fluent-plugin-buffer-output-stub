# This script is very hacky. Use with caution.
#
# Usage: python memory_tracker --docker-image-id='huw3786hf9e,haiufrhy8'
# This will track the RSS usage of a docker container running the image
# 'huw3786hf9e' and 'haiufrhy8'.
#
# The moment this script starts up, it will take a snapshot of which containers
# are running at this point and will only track those containers.
import argparse
import csv
import re
import subprocess
import time
from StringIO import StringIO

def get_container_id_to_image_id_list(allowed_list):
  # Example:
  # $ docker ps --format '{{.ID}},{{.Image}}'
  # 71b673968dc8,us.gcr.io/lingshi-sandbox/buffer-output-stub:fluentd-0.12.43
  # cb99738ca767,us.gcr.io/lingshi-sandbox/buffer-output-stub:fluentd-1.2.3
  ps = subprocess.Popen(
      ('docker', 'ps', '--format', '{{.ID}},{{.Image}}'),
      stdout=subprocess.PIPE)
  result = ps.communicate()[0]
  reader = csv.reader(StringIO(result))
  container_id_to_image_id_list = {}
  for line in reader:
    if line[1] in allowed_list:
      container_id_to_image_id_list[line[0]] = line[1]
  print 'Got container_id_to_image_id_list:\n{}'.format(
      container_id_to_image_id_list)
  return container_id_to_image_id_list

def get_id_to_rss_dict():
  # Example:
  # $ docker stats --no-stream --format '{{.ID}},{{.MemUsage}}'
  # 71b673968dc8,38.28MiB / 29.46GiB
  # cb99738ca767,48MiB / 29.46GiB
  ps = subprocess.Popen(
      ('docker', 'stats', '--no-stream', '--format', '{{.ID}},{{.MemUsage}}'),
      stdout=subprocess.PIPE)
  result = ps.communicate()[0]
  reader = csv.reader(StringIO(result))
  id_to_rss_dict = {}
  for line in reader:
    id_to_rss_dict[line[0]] = re.search("[\d\.]+", line[1]).group(0)
  print 'Got id_to_rss_dict:\n{}'.format(id_to_rss_dict)
  return id_to_rss_dict

parser = argparse.ArgumentParser(
    description='Flags to initiate Memory Tracker.')
parser.add_argument(
    '--docker-image-id', type=str, required=True,
    help='The image id of containers we want to track. If there are more than one, split by comma.')
parser.add_argument(
    '--csv-file-path', type=str, required=True,
    help='The file path to store csv data of RSS usage over time.')
args = parser.parse_args()

allowed_list = args.docker_image_id.split(",")
file_path = args.csv_file_path
container_id_to_image_id_list = get_container_id_to_image_id_list(allowed_list)

with open(file_path, 'a') as csv_file:
  writer = csv.DictWriter(csv_file, fieldnames=list(container_id_to_image_id_list.values()))
  writer.writeheader()

while True:
  with open(file_path, 'a') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=list(container_id_to_image_id_list.values()))
    id_to_rss_dict = get_id_to_rss_dict()
    csv_line = {}
    for container_id, rss in id_to_rss_dict.iteritems():
      if container_id_to_image_id_list.has_key(container_id):
        csv_line[container_id_to_image_id_list[container_id]] = rss
    writer.writerow(csv_line)
  time.sleep(300)
