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

class BrokerService(rpyc.Service):
    def __init__(self):
        self.topics = {}
        self.subscribers = {}

    def create_topic(self, id: UserId, topicname: str) -> Topic:
        topic = f"{id}.{topicname}"
        self.topics[topic] = []
        return topic

    def exposed_login(self, id: UserId, callback) -> bool:
        self.subscribers[id] = callback
        return True

    def exposed_list_topics(self) -> List[Topic]:
        return list(self.topics.keys())

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> bool:
        if topic not in self.topics:
            return False

        content = Content(author=id, topic=topic, data=data)
        self.topics[topic].append(content)

        for subscriber_id, subscriber_callback in self.subscribers.items():
            if subscriber_id != id and self.exposed_subscribe_to(subscriber_id, topic):
                subscriber_callback([content])

        return True

    def exposed_subscribe_to(self, id: UserId, topic: Topic) -> bool:
        if topic not in self.topics:
            return False

        subscriber_topics = self.subscribers.get(id, [])
        if topic not in subscriber_topics:
            subscriber_topics.append(topic)
            self.subscribers[id] = subscriber_topics

        return True

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        if topic not in self.topics:
            return False

        subscriber_topics = self.subscribers.get(id, [])
        if topic in subscriber_topics:
            subscriber_topics.remove(topic)
            self.subscribers[id] = subscriber_topics

        return True

@staticmethod
def create_topic_service(service: BrokerService, id: UserId, topicname: str) -> Topic:
    return service.create_topic(id, topicname)

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    server = ThreadedServer(BrokerService, port=18861)  # Update port if necessary
    server.start()
