from typing import List
from dataclasses import dataclass

import rpyc

UserId = str
Topic = str

@dataclass(frozen=True, kw_only=True, slots=True)
class Content:
    author: UserId
    topic: Topic
    data: str

class PublisherSubscriberService:

    def __init__(self):
        self.connection = rpyc.connect("localhost", 18861)  # Update host and port if necessary

    def create_topic(self, id: UserId, topicname: str) -> Topic:
        return self.connection.root.create_topic(id, topicname)

    def login(self, id: UserId, callback) -> bool:
        return self.connection.root.login(id, callback)

    def list_topics(self) -> List[Topic]:
        return self.connection.root.list_topics()

    def publish(self, id: UserId, topic: Topic, data: str) -> bool:
        return self.connection.root.publish(id, topic, data)

    def subscribe_to(self, id: UserId, topic: Topic) -> bool:
        return self.connection.root.subscribe_to(id, topic)

    def unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        return self.connection.root.unsubscribe_to(id, topic)

def notify_callback(contents: List[Content]):
    for content in contents:
        print(f"New notification: {content.data}")

def main():
    service = PublisherSubscriberService()
    service.login("user1", notify_callback)
    service.create_topic("user1", "topic1")
    service.subscribe_to("user1", "user1.topic1")

    service.publish("user1", "user1.topic1", "Hello, World!")
    service.publish("user2", "user1.topic1", "Hi, user1!")

if __name__ == "__main__":
    main()
