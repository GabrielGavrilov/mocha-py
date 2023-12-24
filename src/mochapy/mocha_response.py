"""
Response class for mocha
"""

class response:
    def __init__(self, views_directory):
        self.__views_directory = views_directory

        self.header = ""
        self.body = ""
    
    """
    Initializes the header with the given status and Content-Type
    """
    def initialize_header(self, status, content_type):
        self.header += f"HTTP/1.0 {status}\r\n"
        self.header += f"Content-Type: {content_type}\r\n"

    """
    Sets the status of the response
    """
    def set_status(self, status):
        if "HTTP/1.0" in self.header:
            pass
        else:
            self.header += f"HTTP/1.0 {status}\r\n"

    """
    Adds an additional header to the  response
    """
    def add_header(self, header, value):
        self.header += f"{header}: {value}\r\n"

    """
    Sets the Content-Type of the response
    """
    def content_type(self, content_type):
        if "Content-Type" in self.header:
            pass
        else:
            self.add_header("Content-Type", content_type)

    """
    Sets the cookie for the response
    """
    def set_cookie(self, name, value):
        self.add_header("Set-Cookie", f"{name}={value}")

    """
    Adds data to the body of the response
    """
    def send(self, data):
        self.body += data
        self.body += "\r\n"

    """
    Renders an entire file to the body for the response
    """
    def render(self, file):
        with open(self.__views_directory + file, "r") as data:
            self.send(data.read())