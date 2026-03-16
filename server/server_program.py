import select
import session
import room

class Program:
    def __init__(self, bind_address):
        self._rooms = {}
        self._sock = self._init_socket(bind_address)
        self._waiting_for_session_initialize = []
    
    def run(self):
        while True:
            readable, _, _ = select.select(self._waiting_for_session_initialize + [self._sock], [], [])
            for sock in readable:
                if sock is self._sock:
                    self._create_new_session_socket(sock)
                else:
                    self._create_session(sock)

            for room in self._rooms.items():
                room.check()
    
    def _create_new_session_socket(self, socket):
        session_socket, _ = socket.accept()
        self._waiting_for_session_initialize.append(session_socket)

    def _initialize_session(self, sock):
        hello_message = sock.recv(1024).decode()
        parsed_hello_message = hello_message.split("\\")
        name = parsed_hello_message[0]
        room_name = parsed_hello_message[1]

        new_session = session.Session(name, sock)
        room = self._get_room(room_name)
        room.add_session(new_session)
        
        self._waiting_for_session_initialize.remove(sock)
    
    def _get_room(self, room_name):
        if room_name in self._rooms.keys():
            return self._rooms[room_name]
        self._rooms[room_name] = room.Room(room_name)
        return self._rooms[room_name]


def main():
    program = Program(("127.0.0.1", 12345))
    program.run()

if __name__ == "__main__":
    main()