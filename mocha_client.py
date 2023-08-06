import mocha_response

class _client:
    def __init__(self, client_connection, client_address, get_routes, views_directory, static_directoy):
        self.connection = client_connection
        self.address = client_address
        self.header = self.connection.recv(1024).decode()
        self.views_directory = views_directory
        self.static_directory = static_directoy

        self.get_routes = get_routes

        self.route = self.__get_requested_route()
        self.method = self.__get_requested_method()

        self.__handle_request()

    def __get_requested_route(self):
        return self.header.split("\r\n")[0].split()[1]
    
    def __get_requested_method(self):
        return self.header.split("\r\n")[0].split()[0]
    
    def __check_for_static_route(self):
        if "." in self.route:
            route_split = self.route.split(".")
            return route_split[len(route_split)-1]
        
        return None

    def __handle_request(self):
        route_type = self.__check_for_static_route()

        if route_type is not None:
            self.__handle_static_route(route_type)

        if self.method == "GET":
            self.__handle_get_request()

    def __handle_static_route(self, route_type):
        if route_type == "css":
            self.__render_static_file("text/css")
        if route_type == "png":
            self.__render_static_image("image/png")
        
    def __render_static_file(self, content_type):
        response = mocha_response.response(self.views_directory, self.static_directory)
        response.initialize("200 OK", content_type)

        file = self.route[1:]
        response.render_static(file)

        self.connection.sendall(str(response).encode())

    def __render_static_image(self, content_type):
        response = mocha_response.response(self.views_directory, self.static_directory)
        response.initialize("200 OK", content_type)
        self.connection.sendall(str(response).encode())

        file = self.route[1:]

        with open(self.static_directory + file, "rb") as data:
            self.connection.sendall(data.read())

    def __handle_get_request(self):
        
        if self.route in self.get_routes:
            callback = self.get_routes.get(self.route)
            self.__handle_get_response(callback)

    def __handle_get_response(self, callback):
        response = mocha_response.response(self.views_directory, self.static_directory)
        callback(response)
        self.connection.sendall(str(response).encode())
        
