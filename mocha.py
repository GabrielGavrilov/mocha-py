import socket
import mocha_client

class mocha:
    def __init__(self):
        self.__get_routes = {}
        self.__views_directory = ""
        self.__static_directory = ""

    def set(self, setting, value):
        if setting == "views":
            self.__views_directory = value
        if setting == "static":
            self.__static_directory = value

    def get(self, path):
        def callback(cb):
            self.__get_routes[path] = cb
            return cb
        
        return callback
    
    def listen(self, port):
        server_socket = socket.socket()
        server_socket.bind(('', port))
        server_socket.listen()

        while True:
            client_connection, client_address = server_socket.accept()
            
            mocha_client._client(
                client_connection, 
                client_address, 
                self.__get_routes, 
                self.__views_directory, 
                self.__static_directory
            )
            
            client_connection.close()

        server_socket.close()