import socket
import select
import sys

EXIT_COMMAND = "/exit"

class ClientProgram:
    def __init__(self, bind_address, name):
        self._name = name
        self._socket = self._init_socket(bind_address)
    
    def _init_socket(self, bind_address):
        sock = socket.socket()
        sock.bind(bind_address)
        return sock
    
    def connect(self, server_address, room_name):
        self._socket.connect(server_address)
        hello_message = f"{self._name}\\{room_name}"
        self._socket.send(hello_message.encode())
    
    def run(self):
        while True:
            # STILL NEED TO ADD MULTI-THREDING FOR I/O
            user_input = input(f"{self._name}: ")
            if user_input == EXIT_COMMAND:
                self._exit_gracefully()
                break
            self._socket.send(user_input.encode())
            readable, _, _ = select.select([self._socket], [], [], 0)
            for sock in readable:
                print(sock.recv(1024).decode())
    
    def _exit_gracefully(self):
        self._socket.send(EXIT_COMMAND.encode())
        self._socket.close()

# ARGV: python program <bind port> <client name> <server ip> <server port> <room name>
def main():
    program = ClientProgram(("127.0.0.1", int(sys.argv[1])),sys.argv[2])
    program.connect((sys.argv[3], int(sys.argv[4])), sys.argv[5])
    program.run()

if __name__ == "__main__":
    main()