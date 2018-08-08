#!/usr/bin/env python

"""Log Generator for the Logging Agent performance testing.

This component generates logs with fixed size at a given rate. It should be run
as a daemon.

To start the generator:
./log_generator.py
or
./log_generator.py --log-size-in-bytes=100 --log-rate=100
"""

import argparse
import random
import sched
import string
import time

# The default collection of characters that we use to generate a random log.
_DEFAULT_CHARS = string.ascii_letters + string.digits


class LogGenerator(object):
  """The log generator that sends logs to the Fluentd in_forward plugin.

  Generates logs with fixed size at a given rate.
  """

  def __init__(self,
               log_size_in_bytes,
               log_rate,
               log_file_path):
    """Constructor.

    Args:
      log_size_in_bytes: int.
        The size of each log entry in bytes for fixed-entry logs.
      log_rate: int.
        The number of expected log entries per second for fixed-rate logs.
      log_file_path: str
        The path of the file to write logs to.
    """
    self._log_rate = log_rate
    self._log_record = self._random_string(log_size_in_bytes)
    self._log_file_path = '{}-{}-'.format(log_file_path, random.randint(1,9999))

  def _random_string(self, size, chars=None):
    """Generates a random string as the log message.

    The string comes with a given size and character collection.

    Args:
      size: int.
        The size of the actual log message in bytes.
      chars: str or None.
        The collection of characters that we use to generate a random string.
    Returns:
      A random string.
    """
    return ''.join(random.choice(chars or _DEFAULT_CHARS) for _ in range(size))

  def send_logs(self):
    """Sends the log message.

    This should be executed every second. Retry if failed.
    """
    for i in range(30):
      with open('{}-{}.log'.format(self._log_file_path, i), 'a') as log_file:
        for _ in range(self._log_rate):
          log_file.write(self._log_record + '\n')


def schedule_event_and_send_logs(scheduler, log_generator_instance):
  """Schedules another event 1 second later and sends logs.

  Args:
    scheduler: scheduler.
      A scheduler that schedules the current event repeatedly.
    log_generator_instance: LogGenerator.
      The log generator instance to create logs.
  """
  scheduler.enter(1, 1, schedule_event_and_send_logs,
                  argument=(scheduler, log_generator_instance))
  log_generator_instance.send_logs()


# Main function.
parser = argparse.ArgumentParser(
    description='Flags to initiate Log Generator.')
parser.add_argument(
    '--log-size-in-bytes', type=int, default=100,
    help='The size of each log entry in bytes for fixed-entry logs.')
parser.add_argument(
    '--log-rate', type=int, default=34,
    help='The number of expected log entries per second for fixed-rate logs.')
parser.add_argument(
    '--log-file-path', type=str, default='/tmp/memory-leak/test',
    help='The path of the file to write logs to.')
args = parser.parse_args()

# Create the socket connection and log generator.
log_generator = LogGenerator(
    args.log_size_in_bytes, args.log_rate, args.log_file_path)

# Use a scheduler to keep sending logs at a steady rate.
event_scheduler = sched.scheduler(time.time, time.sleep)
event_scheduler.enter(1, 1, schedule_event_and_send_logs,
                      argument=(event_scheduler, log_generator))
event_scheduler.run()
