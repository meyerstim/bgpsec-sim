class InvalidASRelFile(Exception):
    def __init__(self, filename: str, message: str):
        self.filename = filename
        self.message = message

class NoRouteError(Exception):
    def __init__(self, message: str):
        self.message = message
