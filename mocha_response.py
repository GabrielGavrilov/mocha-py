class response:
    def __init__(self, views_directory):
        self.__views_directory = views_directory

        self.header = ""
        self.body = ""
    
    def initialize_header(self, status, content_type):
        self.header += f"HTTP/1.0 {status}\r\n"
        self.header += f"Content-Type: {content_type}\r\n"

    def set_status(self, status):
        if "HTTP/1.0" in self.header:
            pass
        else:
            self.header += f"HTTP/1.0 {status}\r\n"

    def add_header(self, header, value):
        self.header += f"{header}: {value}\r\n"

    def content_type(self, content_type):
        if "Content-Type" in self.header:
            pass
        else:
            self.add_header("Content-Type", content_type)

    def set_cookie(self, name, value):
        self.add_header("Set-Cookie", f"{name}={value}")

    def send(self, data):
        self.body += data
        self.body += "\r\n"

    def render(self, file):
        with open(self.__views_directory + file, "r") as data:
            self.send(data.read())