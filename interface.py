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

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(self, id: UserId, topicname: str) -> Topic:
        if topicname in self.topics:
            raise ValueError(f"The topic '{topicname}' already exists.")
        self.topics[topicname] = []
        return topicname

    # Handshake

    def exposed_login(self, username: str) -> Optional[UserId]:
        # Verificar se o usuário já está logado
        for user_id, user_info in self.users.items():
            if user_info.user_name == username:
                return user_id
        # Gerar um novo ID de usuário
        new_user_id = max(self.users.keys(), default=0) + 1
        self.users[new_user_id] = UserInfo(new_user_id, username)
        return new_user_id

    # Query operations

    def exposed_get_user_info(self, id: UserId) -> UserInfo:
        if id not in self.users:
            raise ValueError(f"The user '{id}' doesn't exist.")
        return self.users.get(id)

    def exposed_list_topics(self) -> list[Topic]:
        return list(self.topics.keys())

    # Publisher operations

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> None:
        # Verificar se o tópico existe
        if topic not in self.topics:
            raise ValueError(f"The topic '{topic}' doesn't exist.")
        # Criar o conteúdo do anúncio
        content = Content(id, topic, data)
        # Notificar todos os inscritos no tópico
        subscribers = self.topics[topic]
        for subscriber_id, callback in subscribers:
            callback([(topic, content)])

    # Subscriber operations

    def exposed_subscribe_to(self, id: UserId, topic: Topic, callback: FnNotify) -> Optional[FnNotify]:
        # Verificar se o tópico existe
        if topic not in self.topics:
            raise ValueError(f"The topic '{topic}' doesn't exist.")
        # Verificar se o usuário já está inscrito no tópico
        subscribers = self.topics[topic]
        for subscriber_id, _ in subscribers:
            if subscriber_id == id:
                return "You are already subscribed to this topic."
        # Adicionar o usuário aos inscritos
        self.topics[topic].append((id, callback))
        return callback

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> Optional[FnNotify]:
        # Verificar se o tópico existe
        if topic not in self.topics:
            raise ValueError(f"The topic '{topic}' doesn't exist.")
        # Remover o usuário dos inscritos
        subscribers = self.topics[topic]
        for i, (subscriber_id, callback) in enumerate(subscribers):
            if subscriber_id == id:
                return subscribers.pop(i)[1]
        return "You are not subscribed to this topic."

    # Nota: A semântica do subscribe_all não foi definida, opções:
    # 0 - Jogar essa função fora (e unsubscribe_all)
    # 1 - Se um topico for criado depois, deve inscrever o User nele
    # 2 - Se um topico for criado depois, não deve inscrever o User nele
    #
    # a: nos casos (0) e (2) fazem sentido se inscrever no "evento" de "novo tópico"
    def exposed_subscribe_all(self, id: UserId, callback: FnNotify) -> Optional[FnNotify]:
        # Inscrever o usuário em todos os tópicos existentes
        for topic in self.topics:
            self.exposed_subscribe_to(id, topic, callback)
        return callback

    # Nota: não sei como deve ser o retorno dessa função,
    # talvez: dict[Topic, Optional[FnNotify]]
    def exposed_unsubscribe_all(self, id: UserId) -> FnNotify:
        # Cancelar a inscrição do usuário em todos os tópicos existentes\
        for topic in self.topics:
            self.exposed_unsubscribe_to(id, topic)
        return 'You are not subscribed to any topic anymore.'
