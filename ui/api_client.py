import pika
import json
import uuid
import asyncio
from typing import Dict, Any, Callable

from agent.config import Config

class APIClient:
    """
    Handles communication with the agent backend via RabbitMQ.
    Sends mission requests and receives status updates.
    """

    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.response = None
        self.corr_id = None
        self.status_callbacks: Dict[str, Callable[[Dict[str, Any]], None]] = {}

    def connect(self):
        """
        Establishes a connection to RabbitMQ.
        """
        if self.connection and self.connection.is_open:
            return
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=Config.RABBITMQ_HOST,
                    port=Config.RABBITMQ_PORT,
                    credentials=pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASS)
                )
            )
            self.channel = self.connection.channel()
            print("APIClient connected to RabbitMQ.")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error connecting to RabbitMQ: {e}")
            self.connection = None
            self.channel = None

    def _on_response(self, ch, method, props, body):
        """
        Callback for RPC responses (not used for mission status updates).
        """
        if self.corr_id == props.correlation_id:
            self.response = body

    def _on_status_update(self, ch, method, props, body):
        """
        Callback for mission status updates.
        """
        status_data = json.loads(body)
        mission_id = status_data.get("mission_id")
        if mission_id and mission_id in self.status_callbacks:
            self.status_callbacks[mission_id](status_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming_status_updates(self):
        """
        Starts consuming messages from the mission_status queue.
        This should be run in a separate thread or asyncio task.
        """
        self.connect()
        if not self.channel:
            return

        self.channel.queue_declare(queue=Config.RABBITMQ_QUEUE_MISSION_STATUS, durable=True)
        self.channel.basic_consume(
            queue=Config.RABBITMQ_QUEUE_MISSION_STATUS,
            on_message_callback=self._on_status_update
        )
        print("[*] Waiting for mission status updates...")
        self.channel.start_consuming()

    def send_mission_request(self, mission_data: Dict[str, Any], status_callback: Callable[[Dict[str, Any]], None] = None) -> str:
        """
        Sends a mission request to the agent backend.
        Returns the mission_id.
        """
        self.connect()
        if not self.channel:
            raise ConnectionError("Not connected to RabbitMQ.")

        mission_id = str(uuid.uuid4())
        mission_data["mission_id"] = mission_id

        if status_callback:
            self.status_callbacks[mission_id] = status_callback

        self.channel.queue_declare(queue=Config.RABBITMQ_QUEUE_MISSION_REQUESTS, durable=True)
        self.channel.basic_publish(
            exchange=
            "",
            routing_key=Config.RABBITMQ_QUEUE_MISSION_REQUESTS,
            body=json.dumps(mission_data),
            properties=pika.BasicProperties(delivery_mode=2) # Make message persistent
        )
        print(f"[x] Sent mission request {mission_id}")
        return mission_id

    def close(self):
        """
        Closes the RabbitMQ connection.
        """
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("APIClient connection closed.")


# Example usage (for testing)
async def main():
    client = APIClient()

    def my_status_callback(status_data):
        print(f"Received status update: {status_data}")

    # Start consuming status updates in a separate thread/task
    # For a Streamlit app, you'd typically use st.session_state to manage this
    # and run the consumer in a background thread or a dedicated asyncio task.
    # For this example, we'll just send a request and assume a consumer is running elsewhere.

    mission_request = {
        "target_website": "https://www.example.com",
        "product_identifier": "Test Product",
        "primary_card_id": "card_123",
        "profile_name": "test_user"
    }

    try:
        mission_id = client.send_mission_request(mission_request, my_status_callback)
        print(f"Mission {mission_id} sent. Waiting for updates...")
        # In a real app, you'd have a loop or a mechanism to keep the app alive
        # and process status updates.
        await asyncio.sleep(60) # Keep alive for a minute to receive updates
    except ConnectionError as e:
        print(f"Failed to send mission request: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # This part is for direct testing of APIClient functionality
    # In a Streamlit app, the APIClient would be instantiated and managed by the app.
    # To run this example, ensure RabbitMQ is running and agent/main.py is also running.
    asyncio.run(main())


