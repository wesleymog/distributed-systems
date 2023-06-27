import rpyc
import threading
import json
import argparse
import sys

PORT = 5003
HOST = 'localhost'

UserId = str
Topic = str


class Content:
    def __init__(self, author, topic, data):
        self.author = author
        self.topic = topic
        self.data = data


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if callable(obj):
            return None
        return super().default(obj)


class BrokerService(rpyc.Service):
    def __init__(self):
        self.topics = {}
        self.subscribers = {}
        self.users = {}
        self.lock = threading.Lock()
        self.load_state_from_file()

    def load_state_from_file(self):
        try:
            with open('data.json', 'r') as file:
                data = json.load(file)
                self.users = data.get('users', {})
                self.topics = data.get('topics', {})
        except FileNotFoundError:
            pass

    def save_state_to_file(self):
        data = {
            'users': self.users,
            'topics': self.topics
        }
        with open('data.json', 'w') as file:
            json.dump(data, file, cls=CustomEncoder)

    def threaded_notify(self, topic, content):
        subscribers = self.topics.get(topic, {})
        for subscriber_id, callback in subscribers.items():
            if subscriber_id != content.author:
                callback([content])

    def exposed_login(self, id, callback):
        with self.lock:
            if id in self.users:
                return False
            self.users[id] = callback
            self.save_state_to_file()
        return True

    def exposed_logout(self, id):
        with self.lock:
            if id in self.users:
                del self.users[id]
                self.save_state_to_file()
                return True
        return False

    def exposed_list_topics(self):
        return list(self.topics.keys())

    def exposed_publish(self, id, topic, data):
        if topic not in self.topics:
            return False
        content = Content(id, topic, data)
        with self.lock:
            threading.Thread(target=self.threaded_notify, args=(topic, content)).start()
            self.save_state_to_file()
        return True

    def exposed_subscribe_to(self, id, topic):
        if topic not in self.topics:
            return False
        if id in self.topics[topic]:
            return True
        callback = self.users[id]
        with self.lock:
            self.topics.setdefault(topic, {})
            self.topics[topic][id] = callback
            self.save_state_to_file()
            self.notify_subscribers(topic, created=True)
        return True

    def exposed_unsubscribe_to(self, id, topic):
        if topic in self.topics and id in self.topics[topic]:
            del self.topics[topic][id]
            self.notify_subscribers(topic, created=False)
            self.save_state_to_file()  # Adiciona a chamada para salvar as alterações no arquivo JSON
            return True
        return False


    def create_topic(self, topic: Topic) -> bool:
        with self.lock:
            if topic in self.topics:
                return False
            self.topics[topic] = {}
            self.save_state_to_file()
            self.notify_publishers(topic)  # Notifica os publishers sobre a criação do novo tópico
        return True

    def exposed_create_topic(self, topic: Topic) -> bool:
        return self.create_topic(topic)

    def notify_subscribers(self, topic, created=True):
        if created:
            message = f"Novo tópico criado: {topic}"
        else:
            message = f"Tópico atualizado: {topic}"
        for callback in self.topics[topic].values():
            threading.Thread(target=callback, args=(message,)).start()

def start_server():
    broker = BrokerService()
    server = rpyc.ThreadedServer(broker, port=PORT, hostname=HOST)
    server.start()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--create-topic':
        if len(sys.argv) > 2:
            topic = sys.argv[2]
            conn = rpyc.connect(HOST, PORT)
            success = conn.root.exposed_create_topic(topic)
            conn.close()
            if success:
                print(f"Tópico '{topic}' criado com sucesso.")
            else:
                print(f"O tópico '{topic}' já existe.")
        else:
            print("Por favor, forneça o nome do tópico a ser criado.")
    else:
        start_server()


if __name__ == '__main__':
    main()