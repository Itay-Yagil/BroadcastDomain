import select
import socket
import session
import room

class ServerProgram:
    def __init__(self, bind_address):
        self._rooms = {}
        self._socket = self._init_socket(bind_address)
        self._waiting_for_session_initialize = []
    
    def _init_socket(self, bind_address):
        print("Initializing socket")
        sock = socket.socket()
        sock.bind(bind_address)
        sock.listen()
        return sock
    
    def run(self):
        print("Running...")
        while True:
            readable, _, _ = select.select(self._waiting_for_session_initialize + [self._socket], [], [], 0)
            for sock in readable:
                if sock is self._socket:
                    self._create_new_session_socket(sock)
                else:
                    self._initialize_session(sock)
            
            self._update_rooms()

    def _update_rooms(self):
        rooms_to_remove = []

        for room in self._rooms.values():
            room.check()
            if room.get_session_amount() == 0:
                rooms_to_remove.append(room.get_name())

        for room in rooms_to_remove:
            print(f"Deleting a room: {room}")
            del self._rooms[room]

    def _create_new_session_socket(self, socket):
        print("Creating new session socket...")
        session_socket, _ = socket.accept()
        self._waiting_for_session_initialize.append(session_socket)

    def _initialize_session(self, sock):
        print("Initializing session...")
        hello_message = sock.recv(1024).decode()
        parsed_hello_message = hello_message.split("\\")
        name = parsed_hello_message[0]
        room_name = parsed_hello_message[1]

        new_session = session.Session(name, sock)
        room = self._get_room(room_name)

        print("Adding session to room...")
        room.add_session(new_session)
        self._waiting_for_session_initialize.remove(sock)
        print("Session initialized...")
    
    def _get_room(self, room_name):
        if room_name in self._rooms.keys():
            return self._rooms[room_name]
        self._rooms[room_name] = room.Room(room_name)
        return self._rooms[room_name]


def main():
    program = ServerProgram(("127.0.0.1", 12345))
    program.run()

if __name__ == "__main__":
    main()