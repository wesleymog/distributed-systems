from type_checking import UserId, Topic, Content, FnNotify
from rpyc.utils.server import ThreadedServer
import rpyc
import json

infos = {
    "users": [],
    "topics": [{
            "id": "test",
            "contents": [],
            "users_subscribed": []
        },
        {
            "id": "news",
            "contents": [],
            "users_subscribed": []
        },
        {
            "id": "topic",
            "contents": [],
            "users_subscribed": []
        }],
    "topic_subscribers": [],
    "users_logged": {},
}

class BrokerService(rpyc.Service):
    def create_topic(self, id: UserId, topicname: str) -> Topic:
        topic = Topic(topicname)
        infos["topics"].append({
            "id": topic,
            "contents": [],
            "users_subscribed": []
        })
        return topic
    def exposed_create_topic(self, id: UserId, topicname: str) -> Topic:
        return self.create_topic(id, topicname)

    def exposed_login(self, id: UserId, callback: FnNotify) -> bool:
        if id in infos["users_logged"].keys():
            return False
        infos["users_logged"][id]=callback
        return True

    def exposed_logout(self, id: UserId) -> bool:
        if id in infos["users_logged"].keys():
            del infos["users_logged"][id]
            return True
        return False

    def exposed_list_topics(self) -> list[Topic]:
        return [topic["id"] for topic in infos["topics"]]

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> bool: 
        topic_info = next((t for t in infos["topics"] if t["id"] == topic), None)
        if not topic_info:
            return False
        content = Content(author=id, topic=topic, data=data)
        topic_info["contents"].append(content)

        subscribers = [s for s in topic_info["users_subscribed"]]
        if subscribers:
            for subscriber in subscribers:
                notify_callback = infos["users_logged"].get(str(subscriber))
                if notify_callback:
                    notify_callback([content])
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
    server = ThreadedServer(BrokerService, port=18861, protocol_config={'allow_public_attrs': True})
    server.start()