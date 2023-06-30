import rpyc
import json
from broker import Topic, UserId
from type_checking import UserId, Topic, Content, FnNotify


class PublisherSubscriberService:
    def __init__(self):
        global backgroundServingThread
        self.conn = rpyc.connect("localhost", 18861)
        backgroundServingThread = rpyc.BgServingThread(self.conn)
        
    def login(self):
        self.user_id = input("Digite o seu login: ")
        success = self.conn.root.login(self.user_id, self.callback)
        if success:
            print(f"Usuário {self.user_id} logado com sucesso.")
        else:
            print(f"Usuário {self.user_id} já está logado.")
        return success

    def logout(self):
        success = self.conn.root.logout(self.user_id)

    #TODO mudar para ser usado só pelo admin
    def create_topic(self, topic_name: str) -> Topic:
        return self.conn.root.create_topic(self.user_id, topic_name)

    def list_topics(self) -> list[Topic]:
        return self.conn.root.list_topics()

    def publish(self, topic: Topic, data: str) -> bool:
        success = self.conn.root.publish(self.user_id, topic, data)
        if success:
            print(f"Mensagem publicada no tópico {topic}.")
        else:
            print(f"Tópico {topic} não existe.")

    def subscribe_to(self, topic: Topic) -> bool:
        success = self.conn.root.subscribe_to(self.user_id, topic)
        if success:
            print(f"Inscrição realizada no tópico {topic}.")
        else:
            print(f"Não foi possível se inscrever no tópico {topic}.")

    def unsubscribe_to(self, topic: Topic) -> bool:
        success = self.conn.root.unsubscribe_to(self.user_id, topic)
        if success:
            print(f"Inscrição removida do tópico {topic}.")
        else:
            print(f"Não foi possível cancelar a inscrição do tópico {topic}.")

    def callback(self, contents: list[Content]):
        for content in contents:
            print(f"Nova mensagem no tópico {content.topic}: {content.data} postado por {content.author}")
    def menu(self):
        menu = ("Escolha uma opção.\n"
                "1. Digite 'topicos' para listar os topicos\n"
                "2. Digite 'publicar' para publicar um tópico\n"
                "3. Digite 'inscrever' para se inscrever em um tópico\n"
                "4. Digite 'cancelar' para cancelar a inscrição em um tópico\n"
                "5. Digite 'fim' para encerrar")
        print(menu)

    def main(self):
        isLogged = self.login()
        while not isLogged:
            print("Erro ao logar!\nTente novamente.")
            isLogged = self.login()
        while isLogged:
            self.menu()
            option = input().strip()
            if option == "criar":
                topic_name = input("Digite o nome do tópico: ")
                self.create_topic(topic_name)
            elif option == "topicos":
                topicos = self.list_topics()
                print(topicos)
            elif option == "publicar":
                topic = input("Digite o nome do tópico: ")
                data = input("Digite o conteúdo do tópico: ")
                self.publish(topic, data)
            elif option == "inscrever":
                topic = input("Digite o nome do tópico para se inscrever: ")
                self.subscribe_to(topic)
            elif option == "cancelar":
                topic = input("Digite o nome do tópico para cancelar a inscrição: ")
                self.unsubscribe_to(topic)
            elif option == "fim":
                logout = self.logout()
                if logout: isLogged = False
                break
            else:
                print("Comando inválido. Tente novamente.\n")
        backgroundServingThread.stop()
        self.conn.close()
        
if __name__ == "__main__":
    service = PublisherSubscriberService()
    #service.login()
    service.main()