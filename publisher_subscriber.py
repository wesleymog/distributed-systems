import rpyc
import json
from broker import BrokerService, Content, Topic, UserId

class PublisherSubscriberService:
    def __init__(self):
        self.conn = rpyc.connect("localhost", 18861)
        self.user_id = None

    def login(self, user_id: UserId) -> bool:
        self.user_id = user_id
        return self.conn.root.login(user_id, self.callback)

    def create_topic(self, topic_name: str) -> Topic:
        return self.conn.root.create_topic(self.user_id, topic_name)

    def list_topics(self) -> list[Topic]:
        return self.conn.root.list_topics()

    def publish(self, topic: Topic, data: str) -> bool:
        return self.conn.root.publish(self.user_id, topic, data)

    def subscribe_to(self, topic: Topic) -> bool:
        return self.conn.root.subscribe_to(self.user_id, topic)

    def unsubscribe_to(self, topic: Topic) -> bool:
        return self.conn.root.unsubscribe_to(self.user_id, topic)

    def callback(self, contents: list[str]) -> None:
        print(f"New contents in topic: {contents}")

        for content in contents:
            content_new = json.loads(content)
            print(content_new.get('author'))
            print(f"Um novo item publicado no tópico {content_new.get('topic')} por {content_new.get('author')}: {content_new.get('data')}")

if __name__ == "__main__":
    service = PublisherSubscriberService()
    user_id = "user1"  # Replace with your user ID
    service.login(user_id)

    topic_name = "News"  # Replace with the desired topic name
    service.create_topic(topic_name)

    topics = service.list_topics()
    print(f"Topics: {topics}")

    topic = topics[0]
    service.subscribe_to(topic)

    data = "New article!"
    service.publish(topic, data)

    # Unsubscribe from the topic
    service.unsubscribe_to(topic)

    service.conn.close()
