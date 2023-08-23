import mocha_response
import mocha_request
import mocha_parser

# TODO:
#   [] - Custom IP for server
#   [] - Clean up

class _client:
    def __init__(self, client_connection, client_address, get_routes, post_routes, views_directory, static_directoy):
        self.connection = client_connection
        self.address = client_address
        self.header = self.connection.recv(1024).decode()
        self.views_directory = views_directory
        self.static_directory = static_directoy

        self.get_routes = get_routes
        self.post_routes = post_routes

        self.route = self.__get_requested_route()
        self.method = self.__get_requested_method()

        self.__handle_request()

    def __get_requested_route(self):
        return self.header.split("\r\n")[0].split()[1]
    
    def __get_requested_method(self):
        return self.header.split("\r\n")[0].split()[0]
    
    def __handle_request(self):
        route_type = self.__check_for_static_route()

        if route_type is not None:
            self.__handle_static_route(route_type)

        if self.method == "GET":
            self.__handle_get_request()

        if self.method == "POST":
            self.__handle_post_request()

    def __check_for_static_route(self):
        if "." in self.route:
            route_split = self.route.split(".")
            return route_split[len(route_split)-1]
        
        return None

    def __handle_static_route(self, route_type):
        if route_type == "css":
            self.__render_static_file("text/css")

        if route_type == "png":
            self.__render_static_image("image/png")
        
    def __render_static_file(self, content_type):
        response = mocha_response.response(self.views_directory)
        response.initialize_header("200 OK", content_type)
        file = self.route[1:]
        file_content = ""

        with open(self.static_directory + file, "rb") as data:
            file_content = data.read()

        self.connection.sendall(response.header.encode())
        self.connection.sendall(str("\r\n").encode())
        self.connection.sendall(file_content)

    def __render_static_image(self, content_type):
        response = mocha_response.response(self.views_directory)
        response.initialize_header("200 OK", content_type)
        file = self.route[1:]

        self.connection.sendall(response.header.encode())
        self.connection.sendall(str("\r\n").encode())

        with open(self.static_directory + file, "rb") as data:
            self.connection.sendall(data.read())

    def __handle_get_request(self):
        parsedCallback = self.__get_callback_from_parsed_route(self.route, self.get_routes)

        if parsedCallback is not None:
            self.__handle_parsed_get_response(parsedCallback)
            return

        if self.route in self.get_routes:
            callback = self.get_routes.get(self.route)
            self.__handle_get_response(callback)

        else:
            self.__handle_route_not_found()

    def __handle_post_request(self):
        parsedCallback = self.__get_callback_from_parsed_route(self.route, self.post_routes)

        if parsedCallback is not None:
            self.__handle_parsed_post_response(parsedCallback)
            return

        if self.route in self.post_routes:
            callback = self.post_routes.get(self.route)
            self.__handle_post_response(callback)
        
        else:
            self.__handle_route_not_found()

    def __handle_get_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)
        
        request.header = self.header
        request.cookie = self.__get_cookies()
        
        callback(request, response)
        self.__write_full_response(response)

    def __handle_post_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)
       
        request.header = self.header
        request.cookie = self.__get_cookies()
        request.payload = self.__get_post_payload()

        callback(request, response)
        self.__write_full_response(response)

    def __handle_parsed_get_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)
        template = self.__get_template_from_parsed_route(self.route, self.get_routes)
        parser = mocha_parser.parser(template, self.route)

        request.parameter = parser.parse()
        request.cookie = self.__get_cookies()
        request.header = self.header

        callback(request, response)
        self.__write_full_response(response)

    def __handle_parsed_post_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)
        template = self.__get_template_from_parsed_route(self.route, self.post_routes)
        parser = mocha_parser.parser(template, self.route)

        request.parameter = parser.parse()
        request.payload = self.__get_post_payload()
        request.cookie = self.__get_cookies()
        request.header = self.header

        callback(request, response)
        self.__write_full_response(response)

    def __handle_route_not_found(self):
        for route, callback in self.get_routes.items():
            if route == "*":
                request = mocha_request.request()
                response = mocha_response.response(self.views_directory)
                
                request.cookie = self.__get_cookies()
                request.header = self.header
                
                callback(request, response)
                self.__write_full_response(response)
                return
            
        response = mocha_response.response(self.views_directory)
        response.initialize_header("200 OK", "text/html")
        response.send("<h1>Not Found</h1><p>The requested URL was not found on this server.</p><hr><p>Mocha Python Server</p>")
        self.__write_full_response(response)

    def __get_post_payload(self):
        payload = {}
        header_split = self.header.split("\n")
        for data in header_split:
            if "input" in data.lower():
                raw_payload = data.split("&")
                for raw in raw_payload:
                    payload_data = raw.split("=")
                    payload[payload_data[0]] = payload_data[1]

        return payload
    
    def __get_cookies(self):
        cookies = {}
        header_split = self.header.split("\n")
        for data in header_split:
            if "Cookie" in data:
                cookie_header = data[8:]
                cookies_split = cookie_header.split("; ")
                for cookie in cookies_split:
                    cookie_data = cookie.split("=")
                    cookies[cookie_data[0]] = cookie_data[1]
                    return cookies

    def __get_template_from_parsed_route(self, requested_route, route_list):
        for route, callback in route_list.items():
            parser = mocha_parser.parser(route, requested_route)
            if parser.is_parsable():
                return route
            
        return None

    def __get_callback_from_parsed_route(self, requested_route, route_list):
        for route, callback in route_list.items():
            parser = mocha_parser.parser(route, requested_route)
            if parser.is_parsable():
                return callback
            
        return None

    def __write_full_response(self, response):
        self.connection.sendall(response.header.encode())
        self.connection.sendall(str("\r\n").encode())
        self.connection.sendall(response.body.encode())