from __future__ import annotations
from typing import Callable, TypeAlias
from dataclasses import dataclass
import rpyc

UserId: TypeAlias = str
Topic: TypeAlias = str

@dataclass(frozen=True, kw_only=True, slots=True)
class Content:
    author: UserId
    topic: Topic
    data: str

infos = {
    "users": [],
    "topics": [],
    "topic_subscribers": [],
    "users_logged": {},
}

FnNotify: TypeAlias = Callable[[list[Content]], None]

class BrokerService(rpyc.Service):
    def exposed_create_topic(self, id: UserId, topicname: str) -> Topic:
        topic = Topic(topicname)
        infos["topics"].append({
            "id": topic,
            "contents": [],
            "users_subscribed": []
        })
        return topic

    def exposed_login(self, id: UserId, callback: FnNotify) -> bool:
        infos["users_logged"][id] = callback
        return True

    def exposed_list_topics(self) -> list[Topic]:
        return [topic["id"] for topic in infos["topics"]]

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> bool:
        topic_info = next((t for t in infos["topics"] if t["id"] == topic), None)
        if not topic_info:
            return False
        content = Content(author=id, topic=topic, data=data)
        topic_info["contents"].append(content)

        subscribers = [s for s in topic_info["users_subscribed"]]
        print(topic_info)
        if subscribers:
            notify_callback = infos["users_logged"].get(id)
            if notify_callback:
                notify_callback(['{"author": "'+content.author+'", "topic": "'+content.topic+'", "data": "'+content.data+'"}'])
        return True

    def exposed_subscribe_to(self, id: UserId, topic: Topic) -> bool:
        topic_info = next((t for t in infos["topics"] if t["id"] == topic), None)
        if not topic_info:
            return False
        if id not in topic_info["users_subscribed"]:
            topic_info["users_subscribed"].append(id)
        return True

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        topic_info = next((t for t in infos["topics"] if t["id"] == topic), None)
        if not topic_info:
            return False
        if id in topic_info["users_subscribed"]:
            topic_info["users_subscribed"].remove(id)
        return True


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(BrokerService, port=18861)
    server.start()
