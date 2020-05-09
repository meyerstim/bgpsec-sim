class InvalidASRelFile(Exception):
    def __init__(self, filename, message):
        self.filename = filename
        self.message = message
