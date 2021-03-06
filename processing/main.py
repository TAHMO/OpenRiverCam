import requests
import pika
import traceback
import os
import json
import tasks
import log

logger = log.start_logger(True, False)

# Callback function for each process task that is queued.
def process(ch, method, properties, body):
    try:
        taskInput = json.loads(body.decode("utf-8"))
        task_name = taskInput["type"]
        kwargs = taskInput["kwargs"]
        if hasattr(tasks, task_name):
            task = getattr(tasks, task_name)
            logger.info("Process task of type %s" % taskInput["type"])
            logger.debug(f"kwargs: {kwargs}")
            try:
                task(**kwargs, logger=logger)
                logger.info(f"Task {task_name} was successful")
                # Acknowledge queue item at end of task.
                ch.basic_ack(delivery_tag=method.delivery_tag)
                r = 200
            except BaseException as e:
                logger.error(f"{task_name} failed with error {e}")
                # Acknowledge queue item at end of task.
                ch.basic_ack(delivery_tag=method.delivery_tag)
                requests.post(
                    "{}/processing/error/{}".format(os.getenv("ORC_API_URL"), taskInput["kwargs"]["movie"]["id"]),
                    json={"error_message": str(e)},
                )
                r = 500

    except Exception as e:
        print("Processing failed with error: %s" % str(e))
        traceback.print_tb(e.__traceback__)


connection = pika.BlockingConnection(
    pika.URLParameters('{}?heartbeat=1800&blocked_connection_timeout=900'.format(os.getenv("AMQP_CONNECTION_STRING")))
)
channel = connection.channel()
channel.queue_declare(queue="processing")
# Process a single task at a time.
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="processing", on_message_callback=process)

try:
    print("Start listening for processing tasks in queue.")
    channel.start_consuming()
except Exception as e:
    print("Reboot service due to error: %s" % str(e))
    channel.stop_consuming()
    connection.close()
    traceback.print_tb(e.__traceback__)
