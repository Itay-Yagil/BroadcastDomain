class SessionNotFoundError(LookupError):
    def __init__(self, room_name):
        self.room_name = room_name
    
    def __str__(self):
        return f"{super().__str__()}: An attempt was made to access a session that doesn't exist in room '{self.room_name}'"