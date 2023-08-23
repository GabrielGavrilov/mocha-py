import socket
import time
from threading import Thread
import mocha_client

class mocha:
    def __init__(self):
        self.__get_routes = {}
        self.__post_routes = {}
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
    
    def post(self, path):
        def callback(cb):
            self.__post_routes[path] = cb
            return cb
        
        return callback

    def listen(self, port, host=None):
        Thread(target=self.__listener_thread(port, host), args=(1,)).start()

    def __listener_thread(self, port, host=None):
        server_socket = socket.socket()
        
        if host:
            server_socket.bind((host, port))
        else:    
            server_socket.bind(('', port))
            
        server_socket.listen()

        while True:
            client_connection, client_address = server_socket.accept()
            Thread(target=self.__worker_thread(client_connection, client_address), args=(1,)).start()

        server_socket.close()

    def __worker_thread(self, client_connection, client_address):
        mocha_client._client(
            client_connection, 
            client_address, 
            self.__get_routes, 
            self.__post_routes,
            self.__views_directory, 
            self.__static_directory
        )
            
        client_connection.close()