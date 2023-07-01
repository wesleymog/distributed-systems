from type_checking import UserId, Topic, Content, FnNotify
from rpyc.utils.server import ThreadedServer
import rpyc
import threading

CONTENT_QUEUE_SIZE = 3

infos_lock = threading.Lock()
infos = {
    "users": [],
    "topics": [{
            "id": "estagio",
            "contents": [],
            "users_subscribed": []
        },
        {
            "id": "IC",
            "contents": [],
            "users_subscribed": []
        },
        {
            "id": "monitoria",
            "contents": [],
            "users_subscribed": []
        }],
    "topic_subscribers": [],
    "users_logged": {},
}

class BrokerService(rpyc.Service):
    def create_topic(self, id: UserId, topicname: str) -> Topic:
        # Se o tópico já existe, retorna o tópico
        if topicname in [t["id"] for t in infos["topics"]]:
            return Topic(topicname)
        # Senao, cria o tópico e o retorna
        else:
            with infos_lock:
                topic = Topic(topicname)
                infos["topics"].append({
                    "id": topic,
                    "contents": [],
                    "users_subscribed": []
                })
                return topic

    def exposed_login(self, id: UserId, callback: FnNotify) -> bool:
        with infos_lock:
            if id in infos["users_logged"].keys():
                return False
            infos["users_logged"][id]=callback
            for topic_info in infos["topics"]:
                if id in topic_info["users_subscribed"]:
                    for content_info in topic_info["contents"]:
                        if id not in content_info["users_viewed"]:
                            callback([content_info["content"]])
                            content_info["users_viewed"].append(id)
            return True

    def exposed_logout(self, id: UserId) -> bool:
        with infos_lock:
            if id in infos["users_logged"].keys():
                del infos["users_logged"][id]
                return True
            return False

    def exposed_list_topics(self) -> list[Topic]:
        return [topic["id"] for topic in infos["topics"]]
    
    def exposed_list_subscribed_topics(self, id: UserId) -> list[Topic]:
        return [topic["id"] for topic in infos["topics"] if id in topic["users_subscribed"]]

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> bool: 
        with infos_lock:
            topic_info = next((t for t in infos["topics"] if t["id"] == topic), None)
            if not topic_info:
                return False
            content = Content(author=id, topic=topic, data=data)
            users_subscribed = topic_info["users_subscribed"]
            users_logged_subscribed = [s for s in users_subscribed if str(s) in infos["users_logged"]]
            topic_info["contents"].append({"content":content, "users_viewed":users_logged_subscribed})
            # Se passou do tamanho máximo, remove o anuncio mais antigo
            if len(topic_info["contents"]) > CONTENT_QUEUE_SIZE:
                topic_info["contents"].pop(0)

            subscribers = [s for s in topic_info["users_subscribed"]]
            if subscribers:
                for subscriber in subscribers:
                    notify_callback = infos["users_logged"].get(str(subscriber))
                    if notify_callback:
                        notify_callback([content])
            # print(f'topic_info["contents"]: {topic_info["contents"]}')
            return True

    def exposed_subscribe_to(self, id: UserId, topic: Topic) -> bool:
        with infos_lock:
            topic_info = next((t for t in infos["topics"] if t["id"] == topic), None)
            if not topic_info:
                return False
            if id not in topic_info["users_subscribed"]:
                topic_info["users_subscribed"].append(id)
            return True

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        with infos_lock:
            topic_info = next((t for t in infos["topics"] if t["id"] == topic), None)
            if not topic_info:
                return False
            if id in topic_info["users_subscribed"]:
                topic_info["users_subscribed"].remove(id)
            return True

if __name__ == "__main__":
    server = ThreadedServer(BrokerService, port=18861, protocol_config={'allow_public_attrs': True})
    requests_process = threading.Thread(target=server.start)
    print("Iniciando servidor...")
    requests_process.start()

    while True:
        print("Escolha uma opção:")
        print("1. Digite 'criar' para criar um tópico")
        print("2. Digite 'parar' para parar o servidor")
        option = input("Escreva seu comando: ").strip().lower()

        if option == "criar":
            topicname = input("Digite o nome do tópico: ")
            admin_service = BrokerService()
            topic = admin_service.create_topic("admin", topicname)
            print(f"Tópico '{topicname}' criado com sucesso.\n")
        elif option == "parar":
            server.close()
            requests_process.join()
            break
        else:
            print("Comando inválido. Tente novamente.\n")

