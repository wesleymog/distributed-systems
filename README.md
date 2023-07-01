# Sistema de Anúncios Distribuídos

Este é um projeto de implementação de um sistema de anúncios distribuídos. A aplicação permite que os usuários publiquem anúncios, registrem interesse em anúncios e recebam notificações quando eles ocorrerem, mesmo que não estejam ativos no momento.

## Requisitos Gerais da Aplicação

Um usuário pode realizar as seguintes ações:

1. Criar e publicar anúncios.
2. Registrar interesse em anúncios e receber notificações.
3. Cancelar o registro de interesse em anúncios e deixar de receber notificações.
4. Ao mesmo tempo em que ele cria uma nova notificação ele pode e deve ser notificado se alguém publicar um anúncio que ele tem interesse.

## Arquitetura de Software

A aplicação segue o estilo arquitetural *publish-subscribe*. Os anúncios são identificados por tópicos e possuem atributos, como autor e conteúdo. Os componentes principais da aplicação são:

1. Componente que publica anúncios: cria um anúncio e o envia para o gerente de anúncios.
2. Componente que registra interesse em anúncio: registra interesse em um anúncio no gerente de anúncios e recebe notificação de anúncios.
3. Componente de gerente de anúncios: mantém uma lista de tópicos de anúncios, cria novos tópicos, recebe anúncios para publicação, recebe inscrições de interesse, notifica os usuários registrados e armazena os anúncios até sua expiração.

## Arquitetura de Sistema

A aplicação adota a arquitetura cliente-servidor. O componente de publicação e registro de interesse fica no lado do cliente, enquanto o componente de gerente de anúncios fica no lado do servidor. Ficou decidido em conjunto que o funcionamento consistiria em um único servidor atendendo múltiplos clientes.

## Protocolo de Camada de Aplicação

A aplicação utiliza a camada de middleware RPC (Remote Procedure Call) para a comunicação entre cliente e servidor. O protocolo RPyC (Remote Python Call) é utilizado para facilitar a chamada remota de métodos entre os componentes cliente e servidor.

## Decisões de Implementação
As principais questões que nos deparamos foram:
* Fazer persistência ou não?

    Para poder serializar os métodos de callback seria necessário utilizar outro formato no lugar do JSON, como o arquivos pickle. No entanto, para evitar aumentar a complexidade, decidimos que o PubSub funcionaria apenas de maneira dinâmica, enquanto o servidor estiver ativo (de maneira análoga a uma memória RAM). Na prática, devido à assincronicidade das interações entre inscritos e publicadores, acreditamos que o broker fica de fato ativo o tempo todo, por isso aceitamos essa limitação do nosso modelo.

* Como implementar as opções do administrador?

    Inicialmente pensamos em criar um usuário especial que administraria o servidor por meio de um cliente. No entanto, inspirados pelos laboratórios anteriores, decidimos criar uma Thread específica para o Admin, com o seu comando exclusivo de criar novos tópicos. Para evitar problemas de race condition, utilizamos um Lock em todas as operações que envolvem escrita no dicionário que guarda os dados de usuários, tópicos e anúncios.

## Configuração e Execução

### Pré-requisitos

Certifique-se de ter os seguintes requisitos instalados no seu sistema:

- Python 3.10 ou posterior
- Para versões anteriores do Python (no mínimo 3.7) devem ser usados os arquivos `compatible_server.py` e `compatible_client.py`.
  
### Instalação

Siga as etapas abaixo para executar o sistema de anúncios distribuídos:

1. Clone o repositório em sua máquina local:

```bash
git clone https://github.com/seu-usuario/sistema-anuncios-distribuidos.git
```

2. Acesse o diretório do projeto:
```bash
cd sistema-anuncios-distribuidos
```

3. Crie um ambiente virtual (opcional, mas recomendado) e ative-o:
```bash
python3 -m venv venv
source venv/bin/activate
```

4. Instale as dependências necessárias:
```bash
pip install -r requirements.txt
```

## Uso
1. Inicie o servidor do sistema de anúncios distribuídos executando o arquivo server.py.
```bash
python server.py
```

2. Execute o arquivo client.py para iniciar a interface do cliente no terminal.
```bash
python client.py
```

3. Utilize as opções do menu para interagir com o sistema de anúncios, como fazer login, criar anúncios, inscrever-se em tópicos e receber notificações.

## Autores

- Wesley Mota (@wesleymog)
- Arthur Sasse (@artsasse)
- Lucas Farias (@lukzfarias)

## Licença

Este projeto está licenciado sob a [MIT License](https://opensource.org/licenses/MIT).
