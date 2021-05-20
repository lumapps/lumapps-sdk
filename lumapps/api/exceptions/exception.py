class InvalidUsage(Exception):
    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        error = {"message": self.message}
        return error
