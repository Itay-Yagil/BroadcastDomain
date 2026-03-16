import select
import session

class Room:
    def __init__(self, name):
        self._name = name
        self._sessions = []
        self._interrupts = []

    def check(self):
        sockets = [session.get_socket() for session in self._sessions]
        readable, _, _ = select.select(sockets, [], [])
        for sock in readable:
            received_message = sock.recv(1024).decode()
            current_session = self._sessions.index(sockets.index(sock))
            message_to_send = self._create_message(session, received_message)
            for session in self._sessions:
                if session is not current_session:
                    session.send(message_to_send)
    
    def _create_message(self, session, message):
        return f"{session.get_name()}: {message}"

    def add_session(self, session):
        self._sessions.append(session)