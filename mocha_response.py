class response:
    def __init__(self, views_directory, static_directory):
        self.__views_directory = views_directory
        self.__static_directory = static_directory

        self.header = ""

    def __str__(self):
        return self.header
    
    def initialize(self, status, content_type):
        self.header += f"HTTP/1.0 {status}\r\n"
        self.header += f"Content-Type: {content_type}\r\n\r\n"

    def status(self, status):
        if "HTTP/1.0" in self.header:
            pass
        else:
            self.header += f"HTTP/1.0 {status}\r\n"

    def content_type(self, content_type):
        if "Content-Type" in self.header:
            pass
        else:
            self.header += f"Content-Type: {content_type}\r\n\r\n"

    def send(self, data):
        self.header += data
        self.header += "\r\n"

    def render(self, file):
        with open(self.__views_directory + file, "r") as data:
            self.send(data.read())

    def render_static(self, file):
        with open(self.__static_directory + file, "r") as data:
            self.send(data.read())