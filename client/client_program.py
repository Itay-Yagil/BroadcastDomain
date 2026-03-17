import socket
import select
import sys
import threading

EXIT_COMMAND = "/exit"

class ClientProgram:
    def __init__(self, bind_address, name):
        self._name = name
        self._socket = self._init_socket(bind_address)
        self._is_running = False
    
    def _init_socket(self, bind_address):
        sock = socket.socket()
        sock.bind(bind_address)
        return sock
    
    def connect(self, server_address, room_name):
        self._socket.connect(server_address)
        hello_message = f"{self._name}\\{room_name}"
        self._socket.send(hello_message.encode())
    
    def run(self):
        self._is_running = True
        user_input_thread = threading.Thread(target=self._handle_user_input)
        read_incoming_messages_thread = threading.Thread(target=self._print_incoming_messages)

        user_input_thread.start()
        read_incoming_messages_thread.start()
        

    def _handle_user_input(self):
        while self._is_running:
            user_input = input(f"{self._name}: ")
            if user_input == EXIT_COMMAND:
                self._exit_gracefully()
                self._is_running = False
                break
            self._socket.send(user_input.encode())
    
    def _print_incoming_messages(self):
        while self._is_running:
            readable, _, _ = select.select([self._socket], [], [], 0)
            for sock in readable:
                print(f"\n{sock.recv(1024).decode()}")
    
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