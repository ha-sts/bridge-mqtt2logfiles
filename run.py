#!/usr/bin/env python3

### IMPORTS ###
import argparse
import asyncio
import logging
import os
import sys

from hasts.bridges.utils import MethodTickler
from hasts.bridges.clients import MqttClient
from hasts.bridges.mqtt2logfiles import MessageLogFileManager

### GLOBALS ###

### FUNCTIONS ###
async def wrapper(args):
    logging.debug("Starting wrapper with args: %s", args)
    mqttc = MqttClient(
        host=args.mqtt_host,
        port=args.mqtt_port,
        user=args.username,
        password=args.password
    )
    mlfm = MessageLogFileManager(args.message_file_dir)
    flush_timer = MethodTickler(seconds = 15, corofunc = mlfm.flush)
    rotate_timer = MethodTickler(seconds = 3600, corofunc = mlfm.rotate_file)

    # Create tasks for each worker
    tasks = []
    tasks.append(asyncio.create_task(mqttc.run()))
    tasks.append(asyncio.create_task(flush_timer.run()))
    tasks.append(asyncio.create_task(rotate_timer.run()))
    await asyncio.gather(*tasks)

### CLASSES ###

### MAIN ###
def main():
    # Parse Arguments
    parser = argparse.ArgumentParser(
        description = "Bridge program for logging MQTT events to log files.",
        epilog = "Thank you for using the HA-STS project."
    )
    parser.add_argument("--verbose", action = "store_true", help = "Enable debug logging.")
    parser.add_argument("--username", help = "Username for MQTT server", default = os.getenv("HASTS_MQTT_SERVER_USER"))
    parser.add_argument("--password", help = "Password for MQTT server", default = os.getenv("HASTS_MQTT_SERVER_PASS"))
    parser.add_argument(
        "--mqtt-port",
        help = "MQTT server network port.  Defaults to '1883'.",
        default = os.getenv("HASTS_MQTT_SERVER_PORT", "1883")
    )
    parser.add_argument(
        "--mqtt-host",
        help = "MQTT server hostname or IP address.  Defaults to 'localhost'.",
        default = os.getenv("HASTS_MQTT_SERVER_HOST", "localhost")
    )
    parser.add_argument(
        "--message_file_dir",
        help = "Path to the directory into which the log files will be created.",
        default = os.getenv("HASTS_MESSAGE_FILE_DIR")
    )
    args = parser.parse_args()

    # Setup Logging
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(
        format = log_format,
        level = logging.DEBUG if args.verbose else logging.INFO
    )

    logging.debug("args: %s", args)

    # aiomqtt has moved from https://github.com/sbtinstruments/aiomqtt and https://sbtinstruments.github.io/aiomqtt/
    # aiomqtt is now at https://github.com/empicano/aiomqtt and https://aiomqtt.bo3hm.com/
    # Setting the event loop on "winderps machiens"
    # FIXME: Pretty sure this isn't needed anymore:
    #if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    #    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # NOTE: Moved contents to an async wrapper coroutine to better follow the "high-level" pattern.  This pattern uses
    #       asyncio.run(coro), which handles much, if not all, of the cleanup and interrupts.
    asyncio.run(wrapper(args))

if __name__ == "__main__":
    main()
