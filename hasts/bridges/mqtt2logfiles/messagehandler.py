#!/usr/bin/env python3

### IMPORTS ###
import asyncio
import json
import logging

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MessageHandler:
    def __init__(self, mqtt_client, message_log_file_manager):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("__init__ - mqtt_client: %s, message_log_file_manager: %s", mqtt_client, message_log_file_manager)
        self._mqtt_client = mqtt_client
        self._message_log_file_manager = message_log_file_manager

    async def _handle_message(self, message):
        self.logger.debug("_handle_message - message: %s", message)
        msg_dict = {
            "topic": str(message.topic),
            "payload": str(message.payload.decode('utf-8')),
            "qos": str(message.qos)
        }
        msg_str = str(json.dumps(msg_dict, sort_keys = True))
        await self._message_log_file_manager.write_message(msg_str)

    async def register_coroutines(self):
        # This should be called after the creation of this class to enable listening for messages.
        await self._mqtt_client.register_topic_coroutine("hasts/#", self._handle_message)
