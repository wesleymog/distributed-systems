import rpyc

HOST = 'localhost'
PORT = 5003

class Publisher:
    def __init__(self):
        self.id = None
        self.conn = rpyc.connect(HOST, PORT)
        self.broker = self.conn.root

    def login(self):
        self.id = input("Digite o seu login: ")
        success = self.broker.login(self.id, self.callback)
        if success:
            print(f"Usuário {self.id} logado com sucesso.")
        else:
            print(f"Usuário {self.id} já está logado.")

    def logout(self):
        success = self.broker.logout(self.id)
        if success:
            print(f"Usuário {self.id} deslogado com sucesso.")
        else:
            print(f"Usuário {self.id} não está logado.")

    def publish(self, topic, data):
        success = self.broker.publish(self.id, topic, data)
        if success:
            print(f"Mensagem publicada no tópico {topic}.")
        else:
            print(f"Tópico {topic} não existe.")

    def callback(self, content):
        print("Lista de conteúdos:")
        for item in content:
            print(f"Autor: {item.author}, Tópico: {item.topic}, Dados: {item.data}")

    def menu(self):
        menu = ("Escolha uma opção.\n"
                "1. Digite 'publicar' para publicar um tópico\n"
                "2. Digite 'fim' para encerrar")
        print(menu)

    def main(self):
        while True:
            self.menu()
            option = input().strip()

            if option == "publicar":
                topic = input("Digite o nome do tópico: ")
                data = input("Digite o conteúdo do tópico: ")
                self.publish(topic, data)
            elif option == "fim":
                self.conn.close()
                break
            else:
                print("Comando inválido. Tente novamente.\n")

if __name__ == '__main__':
    publisher = Publisher()
    publisher.login()
    publisher.main()
    publisher.logout()
