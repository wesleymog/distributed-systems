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
        self.users = []

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(self, id: UserId, topicname: str) -> Topic:
        if topicname in self.topics:
            raise ValueError(f"The topic '{topicname}' already exists.")
        self.topics[topicname] = []
        return topicname

    # Handshake

    def exposed_login(self, id: UserId, callback: FnNotify) -> bool:
        # Verificar se o usuário já está logado
        if id in self.users:
            return False
        # Gerar um novo ID de usuário
        new_user_id = max(self.users.keys(), default=0) + 1
        self.users.append(new_user_id)
        return True

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
        for subscriber_id, callback in subscribers:
            callback([(topic, content)])
        return True

    # Subscriber operations

    def exposed_subscribe_to(self, id: UserId, topic: Topic) -> bool:
        # Verificar se o tópico existe
        if topic not in self.topics:
            return False
        # Verificar se o usuário já está inscrito no tópico
        subscribers = self.topics[topic]
        for subscriber_id, _ in subscribers:
            if subscriber_id == id:
                return False
        # Adicionar o usuário aos inscritos
        self.topics[topic].append((id, callback))
        return True

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        # Verificar se o tópico existe
        if topic not in self.topics:
            return True
        # Remover o usuário dos inscritos
        subscribers = self.topics[topic]
        for i, (subscriber_id, callback) in enumerate(subscribers):
            if subscriber_id == id:
                subscribers.pop(i)[1]
                return True
        return False