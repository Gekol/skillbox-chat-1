#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
#  Ctrl + Alt + L - форматирование кода
#
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def send_history(self):
        for message in self.factory.last_ten:
            self.sendLine(message)

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Message from {self.login}: {content}"
            self.factory.last_ten.append(content.encode())
            if len(self.factory.last_ten) == 11:
                self.factory.last_ten.pop(0)
            for user in self.factory.clients:
                user.sendLine(content.encode())
        else:
            # login:admin -> admin
            if content.startswith("login:"):
                self.login = content.replace("login:", "")
                for user in self.factory.clients:
                    if user is not self and user.login == self.login:
                        self.sendLine("Sorry, the login is occupied! Please, try another one!".encode())
                        self.transport.loseConnection()
                        return
                self.sendLine("Welcome!".encode())
                self.send_history()
            else:
                self.sendLine("Invalid login".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    last_ten : list

    def startFactory(self):
        self.clients = []
        self.last_ten = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")

    def send_history(self, client: ServerProtocol):
        client.sendLine("Welcome!".encode())

        last_messages = self.history[-10:]

        for msg in last_messages:
            client.sendLine(msg.encode())


reactor.listenTCP(1234, Server())
reactor.run()
