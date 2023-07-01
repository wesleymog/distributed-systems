import rpyc
from server import Topic
from type_checking import Topic, Content


class PublisherSubscriberService:
    def __init__(self):
        global backgroundServingThread
        self.conn = rpyc.connect("localhost", 18861)
        backgroundServingThread = rpyc.BgServingThread(self.conn)

    def login(self):
        self.user_id = input("Digite o seu login: ")
        success = self.conn.root.login(self.user_id, self.callback)
        if success:
            print(f"Usuário {self.user_id} logado com sucesso.\n")
        else:
            print(f"Usuário {self.user_id} já está logado.\n")
        return success

    def logout(self):
        success = self.conn.root.logout(self.user_id)

    def list_topics(self):
        return self.conn.root.list_topics()
    
    def list_subscribed_topics(self):
        return self.conn.root.list_subscribed_topics(self.user_id)

    def publish(self, topic: Topic, data: str):
        success = self.conn.root.publish(self.user_id, topic, data)
        if success:
            print(f"Mensagem publicada no tópico {topic}.")
        else:
            print(f"Tópico {topic} não existe.")

    def subscribe_to(self, topic: Topic):
        success = self.conn.root.subscribe_to(self.user_id, topic)
        if success:
            print(f"Inscrição realizada no tópico {topic}.\n")
        else:
            print(f"Não foi possível se inscrever no tópico {topic}.\n")

    def unsubscribe_to(self, topic: Topic):
        success = self.conn.root.unsubscribe_to(self.user_id, topic)
        if success:
            print(f"Inscrição removida do tópico {topic}.\n")
        else:
            print(f"Não foi possível cancelar a inscrição do tópico {topic}.\n")

    def callback(self, contents: list[Content]):
        for content in contents:
            print(
                f"Nova mensagem no tópico {content.topic}:\n\"{content.data}\" - postado por {content.author}\n"
            )

    def menu(self):
        menu = (
            f"Olá {self.user_id}! Escolha uma opção.\n"
            "1. Digite 'topicos' para listar os topicos\n"
            "2. Digite 'inscricoes' para listar os tópicos que você está inscrito\n"
            "3. Digite 'publicar' para publicar em um tópico\n"
            "4. Digite 'inscrever' para se inscrever em um tópico\n"
            "5. Digite 'cancelar' para cancelar a inscrição em um tópico\n"
            "6. Digite 'fim' para encerrar\n"
            "7. Digite 'ajuda' para ver este menu novamente\n"
        )
        print(menu)

    def main(self):
        isLogged = self.login()
        while not isLogged:
            print("Erro ao logar!\nTente novamente.")
            isLogged = self.login()
        self.menu()
        while isLogged:
            option = input("Escreva seu comando ('ajuda' para ver o menu): ").strip()
            if option == "topicos":
                topicos = self.list_topics()
                print(f"Os tópicos disponíveis são: {str(topicos)}\n")
            elif option == "inscricoes":
                inscricoes = self.list_subscribed_topics()
                print(f"Os tópicos em que você está inscrito são: {str(inscricoes)}\n")
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
                if logout:
                    isLogged = False
                break
            elif option == "ajuda":
                self.menu()
            else:
                print("Comando inválido. Tente novamente.\n")
        backgroundServingThread.stop()
        self.conn.close()


if __name__ == "__main__":
    service = PublisherSubscriberService()
    service.main()
