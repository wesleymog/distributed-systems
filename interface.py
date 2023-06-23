from __future__ import annotations

from typing import Callable, Optional, Tuple, TypeAlias
from dataclasses import dataclass

import rpyc # type: ignore

UserId: TypeAlias = int

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only
@dataclass(frozen=True, kw_only=True, slots=True)
class UserInfo:
    user_id: UserId
    user_name: str

Topic: TypeAlias = str

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only
@dataclass(frozen=True, kw_only=True, slots=True)
class Content:
    author: UserId
    topic: Topic
    data: str

# Aqui pode ser uma função que recebe apenas um Tuple[Topic, Content]
# ou seja:
# FnNotify: TypeAlias = Callable[[Tuple[Topic, Content]], None]
FnNotify: TypeAlias = Callable[[list[Tuple[Topic, Content]]], None]

class BrokerService(rpyc.Service): # type: ignore
    def __init__(self):
        self.topics = {}
        self.subscribers = {}

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(self, id: UserId, topicname: str) -> Topic:
        if topicname in self.topics:
            raise ValueError(f"The topic '{topicname}' already exists.")
        self.topics[topicname] = []
        return topicname

    # Handshake

    def exposed_login(self, username: str)-> bool:
        # Verificar se o usuário já está logado
        for user_id, user_info in self.users.items():
            if user_info.user_name == username:
                return False
        # Gerar um novo ID de usuário
        new_user_id = max(self.users.keys(), default=0) + 1
        self.users[new_user_id] = UserInfo(new_user_id, username)
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
            return False
        # Remover o usuário dos inscritos
        subscribers = self.topics[topic]
        for i, (subscriber_id, callback) in enumerate(subscribers):
            if subscriber_id == id:
                subscribers.pop(i)[1]
                return True
        return True