from __future__ import annotations

from typing import Callable, TypeAlias
from dataclasses import dataclass

import rpyc # type: ignore

UserId: TypeAlias = str
Topic: TypeAlias = str

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only
@dataclass(frozen=True, kw_only=True, slots=True)
class Content:
    author: UserId
    topic: Topic
    data: str

FnNotify: TypeAlias = Callable[[list[Content]], None]

class BrokerService(rpyc.Service): # type: ignore
    def __init__(self):
        self.topics = {}
        self.subscribers = {}
        self.users = {}

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(self, id: UserId, topicname: str) -> Topic:
        if topicname in self.topics:
            raise ValueError(f"The topic '{topicname}' already exists.")
        self.topics[topicname] = []
        return topicname

    # Handshake

    def exposed_login(self, id: UserId, callback: FnNotify) -> bool:
        # Verificar se o usuário já está logado
        if id in self.users: # TODO: Verificar na lista de usuários logados
            return False
        # Salva o id do usuário associado à sua função de callback
        self.users[id] = callback
        return True
    
    def exposed_logout(self, id: UserId) -> bool:
        # Verificar se o usuário está logado
        if id in self.users:
            del self.users[id]
            return True
        return False


    def exposed_list_topics(self) -> list[Topic]:
        return list(self.topics.keys())

    # Publisher operations

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> bool:
        # Verificar se o tópico existe
        if topic not in self.topics:
            return False
        # Criar o conteúdo do anúncio
        content = Content(id, topic, data)
        # Notificar todos os inscritos no tópico
        subscribers = self.topics[topic]
        for callback in subscribers.values(): # assumindo que subscribers é um dict {UserId: FnNotify}
            callback([content])  # TODO: entrega a posteriori (quando o user nao esta online)
        return True

    # Subscriber operations

    def exposed_subscribe_to(self, id: UserId, topic: Topic) -> bool:
        # Verificar se o tópico existe
        if topic not in self.topics:
            return False
        # Verificar se o usuário já está inscrito no tópico
        if id in self.topics[topic]:
            return True  # TODO: Confirmar o retorno. Pelo que lembro é True quando já está inscrito.
        # TODO: Verificar se o usuário existe? Ou ele só vai usar esse método se já estiver logado?
        # Recuperar a função de callback do usuário
        callback = self.users[id]
        # Adicionar o usuário aos inscritos
        self.topics[topic][id] = callback
        return True

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        # Verificar se o tópico existe
        if topic not in self.topics:
            return True
        # Verificar se o usuário está inscrito no tópico
        if id not in self.topics[topic]:
            return True
        # Remover o usuário dos inscritos
        del self.topics[topic][id]
        return True