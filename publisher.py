import rpyc

HOST = 'localhost'
PORT = 5000

OPCAO_PUBLICAR = 'publicar'
OPCAO_FIM = 'fim'

class Publisher:
    def __init__(self, id):
        self.id = id
        self.conn = rpyc.connect(HOST, PORT)

    def login(self):
        success = self.conn.exposed_login(self.id, self.callback)
        print(f"Usuário {self.id} logado com sucesso.") if success else print(f"Usuário {self.id} já está logado.")

    def logout(self):
        success = self.conn.exposed_logout(self.id)
        print(f"Usuário {self.id} deslogado com sucesso.") if success else print(f"Usuário {self.id} não está logado.")
    
    def publish(self, topic, data):
        success = self.conn.exposed_publish(self.id, topic, data)
        if not success:
            print(f"Tópico {topic} não existe.")

    def callback(self, content):
        print("Lista de conteúdos:")
        print(content)
    
    def menu(self):
        menu = ("Escolha uma opção.\n"
				"1. Digite 'publicar' para publicar um tópico\n"
				"2. Digite 'fim' para encerrar")
        print(menu)
    
    def main(self):
        while True:
            self.menu()
            option = input().strip()
            
            if option == OPCAO_PUBLICAR:
                topic = input("Digite o nome do tópico: ")
                data = input("Digite o conteúdo do tópico: ")
                self.publish(topic, data)
            elif option == OPCAO_FIM:
                self.conn.close()
                break
            else:
                print("Comando inválido. Tente novamente.\n")

if __name__ == '__main__':
    pub_id = input("Digite seu login: ")
    publisher = Publisher(pub_id)
    publisher.main()