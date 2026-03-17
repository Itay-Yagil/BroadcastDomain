class Session:
    def __init__(self, name, socket):
        self._name = name
        self._socket = socket
    
    def get_name(self):
        return self._name
    
    def get_socket(self):
        return self._socket
    
    def send(self, data):
        self._socket.send(data)

    def close(self):
        self._socket.close()