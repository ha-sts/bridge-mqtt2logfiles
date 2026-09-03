#!/usr/bin/env python3

### IMPORTS ###
import datetime
import logging
import pathlib

from .messagelogfile import MessageLogFile

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
# FIXME: Need a coroutine that triggers the flush every 15 seconds or so.
# FIXME: How to do the file rotation?
class MessageLogFileManager:
    def __init__(self, message_directory_path):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - message_directory_path: %s", message_directory_path)
        self.message_directory_path = pathlib.Path(message_directory_path)
        self.message_file = self._open_file()

    def _open_file(self):
        self.logger.debug("_open_file")
        dt = datetime.datetime.now(datetime.timezone.utc)
        dt = dt - datetime.timedelta(microseconds = dt.microsecond)
        dt_str = dt.isoformat()
        file_path = pathlib.Path(self.message_directory_path, "mqtt_messages_{}.json.log".format(dt_str))
        self.logger.debug("file_path to open: %s", file_path)
        return MessageLogFile(file_path)

    async def rotate_file(self):
        self.logger.debug("rotate_file")
        # This should do an "atomic swap" or properly known as a tuple swap.
        old_file, self.message_file = self.message_file, self._open_file()
        await old_file.flush()

    async def write_line(self, message):
        self.logger.debug("write_message - message: %s", message)
        await self.message_file.write_message(message)

    async def flush(self):
        self.logger.debug("flush")
        # FIXME: Is this where the rotation should be checked?
        await self.message_file.flush()

