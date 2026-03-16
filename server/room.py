import select

EXIT_COMMAND = "/exit"

class Room:
    def __init__(self, name):
        self._name = name
        self._sessions = []
        self._interrupts = []
    
    def get_name(self):
        return self._name

    def check(self):
        sockets = [session.get_socket() for session in self._sessions]
        readable, _, _ = select.select(sockets, [], [], 0)
        for sock in readable:
            print("readable socket!")
            current_session = self._sessions[sockets.index(sock)]
            received_message = sock.recv(1024).decode()
            print(f"{received_message}")

            if received_message == EXIT_COMMAND:
                current_session.close()
                self._sessions.remove(current_session)
            else:
                message_to_send = self._create_message(current_session, received_message)
                for session in self._sessions:
                    if session is not current_session:
                        print(f"{self._name} - {message_to_send}")
                        session.send(message_to_send.encode())
    
    def get_session_amount(self):
        return len(self._sessions)
    
    def _create_message(self, session, message):
        return f"{session.get_name()}: {message}"

    def add_session(self, session):
        self._sessions.append(session)
        print(f"Current session: {self._sessions}")