#!/bin/bash

# Cleaning up previous residues.
TEST_DIR='/tmp/fluentd-memory-leak12345'
rm -rf $TEST_DIR
kill $(ps -aux | grep "python $TEST_DIR/fluent-plugin-buffer-output-stub" | grep -v "grep" | awk '{print $2}')

# Check out the repo.
# If you want to change $TEST_DIR, the fluent.conf file needs to be changed accordingly.
mkdir -p $TEST_DIR
chmod 777 $TEST_DIR
cd $TEST_DIR
git clone https://github.com/qingling128/fluent-plugin-buffer-output-stub.git

# Build the fluent-plugin-buffer-output-stub gem.
cd $TEST_DIR/fluent-plugin-buffer-output-stub
gem build fluent-plugin-buffer-output-stub.gemspec

# Build the Fluentd docker image.
mv fluent-plugin-buffer-output-stub-*.gem docker/
cd $TEST_DIR/fluent-plugin-buffer-output-stub/docker
DOCKER_IMAGE_ID=`docker build --no-cache . | tail -n 1 | sed 's/Successfully built //g'`

# Start the Log Generator.
nohup python $TEST_DIR/fluent-plugin-buffer-output-stub/log_generator.py --log-rate=34 --log-file-path="$TEST_DIR/test" &
sleep 2
chmod 777 $TEST_DIR/*.log

# Start fluentd.
docker run -d -v $TEST_DIR:$TEST_DIR $DOCKER_IMAGE_ID
sleep 2

# Start memory tracker.
nohup python $TEST_DIR/fluent-plugin-buffer-output-stub/memory_tracker.py --docker-image-id=$DOCKER_IMAGE_ID --csv-file-path=$TEST_DIR/rss_usage_over_time.csv &
