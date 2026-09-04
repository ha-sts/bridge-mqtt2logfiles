#!/usr/bin/env python3

### IMPORTS ###
import aiofiles
import asyncio
import logging

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MessageLogFile:
    def __init__(self, message_file_path):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("__init__ - message_file_path: %s", message_file_path)
        self.message_file_path = message_file_path
        self.queue = asyncio.Queue()

    async def write_message(self, message):
        self.logger.debug("write_message - message: %s", message)
        await self.queue.put(str(message))

    async def flush(self):
        # FIXME: Handle exceptions from file handling here
        self.logger.debug("flush")
        async with aiofiles.open(self.message_file_path, 'a') as message_file:
            while not self.queue.empty():
                message = await self.queue.get()
                await message_file.write("{}\n".format(message))

    def __del__(self):
        self.logger.debug("__del__")
        self.flush()
