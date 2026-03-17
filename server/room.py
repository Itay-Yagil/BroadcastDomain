import select
import exceptions

EXIT_COMMAND = "/exit"
TRASNFER_ROOM_COMMAND = "/transfer"

class Room:
    def __init__(self, name):
        self._name = name
        self._sessions = []
        self._interrupts = []
    
    def add_session(self, session):
        print(f"Adding new session to room: {self._name}")
        self._sessions.append(session)
    
    def remove_session(self, session):
        self._sessions.remove(session)

    def check(self):
        sockets = [session.get_socket() for session in self._sessions]

        if sockets == []:
            return

        readable, _, _ = select.select(sockets, [], [], 0)
        for sock in readable:
            self._handle_readable_socket(sock)

    def _handle_readable_socket(self, sock):
        received_message = sock.recv(1024).decode()
        print(f"{received_message}")
        current_session = self._get_session_by_socket(sock)

        if received_message.startswith("/"):
            self._client_commands_handler(received_message, current_session)
        else:
            message_to_send = self._create_message(current_session.get_name(), received_message)
            self._broadcast_message(message_to_send, current_session)

    def _get_session_by_socket(self, sock):
        for session in self._sessions:
            if session.get_socket() is sock:
                return session
        raise exceptions.SessionNotFoundError(self._name)
    
    def _client_commands_handler(self, command, session):
        if command == EXIT_COMMAND:
            session.close()
            self._sessions.remove(session)
        elif command.split()[0] == TRASNFER_ROOM_COMMAND and len(command.split()) >= 2 and \
             command.split()[1] != self._name:
            self._interrupts.append((session, command.split()[1]))

    def _broadcast_message(self, message, sender_session):
        for session in self._sessions:
            if session is not sender_session:
                print(f"{self._name} - {message}")
                session.send(message.encode())
    
    def broadcast(self, admin, message):
        message_to_send = self._create_message(admin, message)
        for session in self._sessions:
            session.send(message_to_send.encode())
    
    def _create_message(self, name, message):
        return f"{name}: {message}"

    def get_name(self):
        return self._name
    
    def get_session_amount(self):
        return len(self._sessions)
    
    def get_interrupts_copy(self):
        return self._interrupts.copy()
    
    def remove_interrupt(self, interrupt):
        self._interrupts.remove(interrupt)