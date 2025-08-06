import asyncio
import json
import pika
import os
from agent.config import Config
from agent.brain.orchestrator import Orchestrator

# Initialize Orchestrator outside the consumer to maintain state
orchestrator = Orchestrator()

def callback(ch, method, properties, body):
    """
    Callback function to process messages from the mission_requests queue.
    """
    mission_data = json.loads(body)
    mission_id = mission_data.get("mission_id", "unknown_mission")
    print(f"[x] Received mission request: {mission_id}")

    # Acknowledge the message immediately to prevent re-delivery on long processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

    async def run_mission_async():
        try:
            # Run the mission using the orchestrator
            result = await orchestrator.run_mission(mission_data)
            print(f"[x] Mission {mission_id} completed with status: {result.get("status")}")
            
            # Publish mission status back to the UI/client
            publish_status(result)

        except Exception as e:
            print(f"[!] Error processing mission {mission_id}: {e}")
            error_result = {
                "mission_id": mission_id,
                "status": "failed",
                "outcome": "internal_error",
                "message": str(e)
            }
            publish_status(error_result)

    # Run the async mission in a new event loop or existing one
    # For simplicity in a blocking pika consumer, we create a new loop.
    # In a more complex async application, you'd integrate with an existing loop.
    loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_mission_async())

def publish_status(status_data):
    """
    Publishes mission status to the mission_status queue.
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASS)
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue=Config.RABBITMQ_QUEUE_MISSION_STATUS, durable=True)
        channel.basic_publish(
            exchange="",


            routing_key=Config.RABBITMQ_QUEUE_MISSION_STATUS,
            body=json.dumps(status_data),
            properties=pika.BasicProperties(delivery_mode=2) # Make message persistent
        )
        print(f"[x] Published mission status for {status_data.get("mission_id")}")
        connection.close()
    except Exception as e:
        print(f"[!] Error publishing status: {e}")

def main():
    print("[*] Agent starting up...")
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASS)
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue=Config.RABBITMQ_QUEUE_MISSION_REQUESTS, durable=True)
        channel.basic_qos(prefetch_count=1) # Process one message at a time
        channel.basic_consume(queue=Config.RABBITMQ_QUEUE_MISSION_REQUESTS, on_message_callback=callback)

        print("[*] Waiting for mission requests. To exit press CTRL+C")
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"[!] Could not connect to RabbitMQ: {e}")
        print("Please ensure RabbitMQ is running and accessible.")
    except KeyboardInterrupt:
        print("[*] Agent shutting down.")
    except Exception as e:
        print(f"[!] An unexpected error occurred in main: {e}")

if __name__ == "__main__":
    main()


