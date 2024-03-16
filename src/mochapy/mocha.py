import socket
import time
from threading import Thread
from mochapy import mocha_client

"""
Mocha - A tiny flexible web server framework for Python
@author Gabriel Gavrilov <gabriel.gavrilov02@gmail.com>
"""

class mocha:
    def __init__(self):
        self.__get_routes = {} # GET routes
        self.__post_routes = {} # POST routes
        self.__put_routes = {} # PUT routes
        self.__delete_routes = {} # DELETE routes
        self.__views_directory = "" # views directory
        self.__static_directory = "" # static directroy

    """
    Used to set the mocha server settings
    """
    def set(self, setting, value):
        if setting == "views":
            self.__views_directory = value
        if setting == "static":
            self.__static_directory = value

    """
    Creates a GET route. Stores the route and its callback in a dictionary.
    Gets used by the mocha_client class
    """
    def get(self, path):
        def callback(cb):
            self.__get_routes[path] = cb
            return cb
        return callback
    
    """
    Creates a POST route. Stores the route and its callback in a dictionary.
    Gets used by the mocha_client class
    """
    def post(self, path):
        def callback(cb):
            self.__post_routes[path] = cb
            return cb
        return callback
    
    """
    Creates a GET routes. Stores the route and its callback in a dictionary.
    Gets used by the mocha_client class
    """
    def put(self, path):
        def callback(cb):
            self.__put_routes[path] = cb
            return cb
        return callback
    
    """
    Creates a GET routes. Stores the route and its callback in a dictionary.
    Gets used by the mocha_client class
    """
    def delete(self, path):
        def callback(cb):
            self.__delete_routes[path] = cb
            return cb
        return callback

    """
    Starts the mocha web server at the given port and host (not required)
    and listens for new socket connections
    """
    def listen(self, port, host=None):
        def callback(cb):
            cb()
            # create a listener thread
            Thread(target=self.__listener_thread(port, host), args=(1,)).start()

        return callback

    def start(self, port, host=None):
        Thread(target=self.__listener_thread(port, host), args=(1,)).start()

    """
    mocha server listener thread
    """
    def __listener_thread(self, port, host=None):
        server_socket = socket.socket()
        
        if host:
            server_socket.bind((host, port))
        else:    
            server_socket.bind(('', port))
            
        server_socket.listen()

        # Keep listening forever
        while True:
            # accept incoming sockets
            client_connection, client_address = server_socket.accept()
            # create a worker thread
            Thread(target=self.__worker_thread(client_connection, client_address), args=(1,)).start()

        server_socket.close()

    """
    mocha server worker thread
    """
    def __worker_thread(self, client_connection, client_address):
        # creates a new client connection ans passes all the required information for the client to work properly
        mocha_client._client(
            client_connection, 
            client_address, 
            self.__get_routes, 
            self.__post_routes,
            self.__put_routes,
            self.__delete_routes,
            self.__views_directory, 
            self.__static_directory
        )
            
        client_connection.close()