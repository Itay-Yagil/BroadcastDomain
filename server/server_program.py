import select
import socket
import session
import room

class ServerProgram:
    def __init__(self, bind_address):
        self._rooms = {}
        self._socket = self._init_socket(bind_address)
        self._admin_connection = []
        self._waiting_for_session_initialize = []

    def _init_socket(self, bind_address):
        print("Initializing socket...")
        sock = socket.socket()
        sock.bind(bind_address)
        sock.listen()
        return sock

    def run(self):
        print("Running...")
        while True:
            readable, _, _ = select.select(self._waiting_for_session_initialize + self._admin_connection + [self._socket], [], [], 0)
            for sock in readable:
                if sock is self._socket:
                    self._create_new_session_socket(sock)
                elif sock in self._waiting_for_session_initialize:
                    self._initialize_session(sock)
                elif sock in self._admin_connection:
                    self._handle_admin_message(sock)

            self._handle_room_interrupts()
            self._update_room_list()

    def _handle_room_interrupts(self):
        rooms = list(self._rooms.values())
        for room in rooms:
            interrupts = room.get_interrupts_copy()
            for interrupt in interrupts:
                room.remove_session(interrupt[0])
                new_room = self._get_room(interrupt[1])
                new_room.add_session(interrupt[0])

    def _update_room_list(self):
        rooms_to_remove = []

        for room in self._rooms.values():
            room.check()
            if room.get_session_amount() == 0:
                rooms_to_remove.append(room.get_name())

        for room in rooms_to_remove:
            print(f"Deleting a room: {room}...")
            del self._rooms[room]

    def _create_new_session_socket(self, socket):
        print("Creating new session socket...")
        session_socket, _ = socket.accept()
        self._waiting_for_session_initialize.append(session_socket)

    def _initialize_session(self, sock):
        print("Initializing session...")
        hello_message = sock.recv(1024).decode()
        hello_message_fields_dict = self._parse_hello_message(hello_message)

        if hello_message_fields_dict["name"] == "admin":
            self._handle_new_admin_connection(sock)
        else:
            self._handle_new_user_connection(sock, hello_message_fields_dict["name"], hello_message_fields_dict["room_name"])
        
        self._waiting_for_session_initialize.remove(sock)
        print("Session initialized...")

    def _parse_hello_message(self, hello_message):
        parsed_hello_message = hello_message.split("\\")
        hello_message_fields = { "name" : parsed_hello_message[0], 
                                 "room_name" : parsed_hello_message[1]
                               }

        return hello_message_fields
    
    def _handle_new_admin_connection(self, sock):
        self._admin_connection.append(sock)

    def _handle_new_user_connection(self, sock, name, room_name):
        new_session = session.Session(name, sock)
        room = self._get_room(room_name)
        room.add_session(new_session)

    def _get_room(self, room_name):
        if room_name in self._rooms.keys():
            return self._rooms[room_name]
        print(f"Creating a room: {room_name}...")
        self._rooms[room_name] = room.Room(room_name)
        return self._rooms[room_name]

    def _handle_admin_message(self, sock):
        message = sock.recv(1024).decode()
        if message == "/exit":
            self._admin_connection.remove(sock)
        else:
            for room in self._rooms.values():
                room.broadcast("admin", message)


def main():
    program = ServerProgram(("127.0.0.1", 12345))
    program.run()

if __name__ == "__main__":
    main()