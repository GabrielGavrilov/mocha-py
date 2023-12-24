from mochapy import mocha_response
from mochapy import mocha_request
from mochapy import mocha_parser

"""
Reads the socket's requested HTTP header and determines the response based
on the method and route
"""

class _client:
    """
    Sets up the _client class
    """
    def __init__(
            self,
            client_connection,
            client_address,
            get_routes,
            post_routes,
            put_routes,
            delete_routes,
            views_directory,
            static_directoy
        ):
        self.connection = client_connection
        self.address = client_address
        self.header = self.connection.recv(1024).decode() # decodes the header into a string
        self.views_directory = views_directory
        self.static_directory = static_directoy

        self.get_routes = get_routes
        self.post_routes = post_routes
        self.put_routes = put_routes
        self.delete_routes = delete_routes

        self.route = self.__get_requested_route() # gets the requested route from client
        self.method = self.__get_requested_method() # gets the requested route method from client

        self.__handle_request()

    """
    Returns the requested route
    """
    def __get_requested_route(self):
        return self.header.split("\r\n")[0].split()[1]
    
    """
    Returns the requested method
    """
    def __get_requested_method(self):
        return self.header.split("\r\n")[0].split()[0]
    
    """
    Handles the request
    """
    def __handle_request(self):
        # checks if the route is a static route (.css, .png, etc)
        route_type = self.__check_for_static_route()

        if route_type is not None:
            self.__handle_static_route(route_type)

        if self.method == "GET":
            self.__handle_get_request()

        if self.method == "POST":
            self.__handle_post_request()

        if self.method == "PUT":
            self.__handle_put_request()

        if self.method == "DELETE":
            self.__handle_delete_request()

    """
    Returns the file type for the static route
    """
    def __check_for_static_route(self):
        if "." in self.route:
            route_split = self.route.split(".")
            return route_split[len(route_split)-1]
        
        return None

    """
    Handles the static route
    """
    def __handle_static_route(self, route_type):
        if route_type == "css":
            self.__render_static_file("text/css")

        if route_type == "png":
            self.__render_static_image("image/png")
    
    """
    Renders a static file with the given Content-Type
    """
    def __render_static_file(self, content_type):
        response = mocha_response.response(self.views_directory) # creates new response
        response.initialize_header("200 OK", content_type) # initializes the response header with the given content-type 
        file = self.route[1:] # gets the file name
        file_content = "" # gets the file content

        # read the file file in binary
        with open(self.static_directory + file, "rb") as data:
            file_content = data.read()

        # render the file
        self.connection.sendall(response.header.encode())
        self.connection.sendall(str("\r\n").encode())
        self.connection.sendall(file_content)

    """
    Renders a static image with the given Conent-Type
    """
    def __render_static_image(self, content_type):
        response = mocha_response.response(self.views_directory) # creates a new response
        response.initialize_header("200 OK", content_type) # initializes a response header with the given content-type
        file = self.route[1:] # gets the file name

        self.connection.sendall(response.header.encode()) # send the response header
        self.connection.sendall(str("\r\n").encode())

        # send the image's binary to the response
        with open(self.static_directory + file, "rb") as data:
            self.connection.sendall(data.read())

    """
    Handles the GET request
    """
    def __handle_get_request(self):
        # gets a parsed callback if the route has parameters
        parsedCallback = self.__get_callback_from_parsed_route(self.route, self.get_routes)

        # if the route has parameters
        if parsedCallback is not None:
            self.__handle_parsed_get_response(parsedCallback)
            return

        # if the route exists
        if self.route in self.get_routes:
            callback = self.get_routes.get(self.route)
            self.__handle_get_response(callback)

        # otherwise if the route doesn't exist, respond with a 404 page
        else:
            self.__handle_route_not_found()

    """
    Handles the POST request
    """
    def __handle_post_request(self):
        # gets a parsed callback if the route has parameters
        parsedCallback = self.__get_callback_from_parsed_route(self.route, self.post_routes)

        # if the route has parameters
        if parsedCallback is not None:
            self.__handle_parsed_post_response(parsedCallback)
            return

        # if the route exists
        if self.route in self.post_routes:
            callback = self.post_routes.get(self.route)
            self.__handle_post_response(callback)
        
        # otherwise if the route doesn't exist, respond with a 404 page
        else:
            self.__handle_route_not_found()

    """
    Handles the PUT request
    """
    def __handle_put_request(self):
        # gets a parsed callback if the route has parameters
        parsed_callback = self.__get_callback_from_parsed_route(self.route, self.put_routes)

        # if the route has parameters
        if parsed_callback is not None:
            self.__handle_parsed_put_response(parsed_callback)
            return
        
        # if the route exists
        if self.route in self.put_routes:
            callback = self.put_routes.get(self.route)
            self.__handle_put_response(callback)

        # otherwise if the route doesn't exist, respond with a 404 page
        else:
            self.__handle_route_not_found()

    """
    Handles the DELETE request
    """
    def __handle_delete_request(self):
        # gets a parsed callback if the route has parameters
        parsed_callback = self.__get_callback_from_parsed_route(self.route, self.delete_routes)

        # if the route has parameters
        if parsed_callback is not None:
            self.__handle_parsed_delete_response(parsed_callback)
            return
        
        # if the route exists
        if self.route in self.delete_routes:
            callback = self.delete_routes.get(self.route)
            self.__handle_delete_response(callback)

        # otherwise if the route doesn't exist, respond with a 404 page
        else:
            self.__handle_route_not_found()

    """
    Handles the unparsed GET response
    """
    def __handle_get_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)
        
        request.header = self.header # sets the request headers
        request.cookie = self.__get_cookies() # sets the request cookies
        
        callback(request, response) # execute the callback
        self.__write_full_response(response) # write the response to the client

    """
    Handles the unparsed POST response
    """
    def __handle_post_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)
       
        request.header = self.header
        request.cookie = self.__get_cookies() # sets the request cookies
        request.payload = self.__get_body_payload() # sets the request body payload

        callback(request, response) # execute the callback
        self.__write_full_response(response) # write the response to the client

    """
    Handles the unparsed PUT response
    """
    def __handle_put_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)

        request.header = self.header
        request.cookie = self.__get_cookies() # sets the request cookies
        request.payload = self.__get_body_payload() # sets the request payload

        callback(request, response) # execute the callback
        self.__write_full_response(response) # write the response to the client

    """
    Handles the unparsed DELETE response
    """
    def __handle_delete_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)

        request.header = self.header
        request.cookie = self.__get_cookies() # sets the request cookies
        request.payload = self.__get_body_payload() # sets the request payload

        callback(request, response) # executes the callback
        self.__write_full_response(response) # writes the response to the client

    """
    Handles the parsed GET response
    """
    def __handle_parsed_get_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)
        template = self.__get_template_from_parsed_route(self.route, self.get_routes) # gets the template route
        parser = mocha_parser.parser(template, self.route) # parses the route 

        request.parameter = parser.parse() # sets the request route parameters
        request.cookie = self.__get_cookies() # sets the request cookies
        request.header = self.header

        callback(request, response)
        self.__write_full_response(response)

    """
    Handles the parsed POST response
    """
    def __handle_parsed_post_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)
        template = self.__get_template_from_parsed_route(self.route, self.post_routes) # gets the template route
        parser = mocha_parser.parser(template, self.route) # parses the route

        request.parameter = parser.parse() # sets the request route parameters
        request.payload = self.__get_body_payload() # sets the request body payload
        request.cookie = self.__get_cookies() # sets the request cookies
        request.header = self.header

        callback(request, response)
        self.__write_full_response(response)

    """
    Handles the parsed PUT response
    """
    def __handle_parsed_put_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)
        template = self.__get_template_from_parsed_route(self.route, self.put_routes) # gets the template route
        parser = mocha_parser.parser(template, self.route) # parses the route

        request.parameter = parser.parse() # sets the request route parameters
        request.payload = self.__get_body_payload() # sets the request body payload
        request.cookie = self.__get_cookies() # sets the request cookies
        request.header = self.header

        callback(request, response)
        self.__write_full_response(response)

    """
    Handles the parsed DELETE response
    """
    def __handle_parsed_delete_response(self, callback):
        request = mocha_request.request()
        response = mocha_response.response(self.views_directory)
        template = self.__get_template_from_parsed_route(self.route, self.put_routes) # gets the template route
        parser = mocha_parser.parser(template, self.route) # parses the route

        request.parameter = parser.parse() # sets the request route parameters
        request.payload = self.__get_body_payload() # sets the request body payload
        request.cookie = self.__get_cookies() # sets the request cookies
        request.header = self.header

        callback(request, response)
        self.__write_full_response(response)

    """
    Handles the "route not found" response
    """
    def __handle_route_not_found(self):
        for route, callback in self.get_routes.items():
            # users may use their own custom 404 pages if the define a route with an astrisk 
            if route == "*":
                request = mocha_request.request()
                response = mocha_response.response(self.views_directory)
                
                request.cookie = self.__get_cookies()
                request.header = self.header
                
                callback(request, response)
                self.__write_full_response(response)
                return
        
        # if users did not set their own custom 404 page, mocha will respond with a default 404 response
        response = mocha_response.response(self.views_directory)
        response.initialize_header("200 OK", "text/html")
        response.send("<h1>Not Found</h1><p>The requested URL was not found on this server.</p><hr><p>Mocha Python Server</p>")
        self.__write_full_response(response)

    """
    Returns the request body payload
    """
    def __get_body_payload(self):
        payload = {}
        header_split = self.header.split("\n")
        for data in header_split:
            # payload key must have "input" in its name for mocha-py to find it
            if "input" in data.lower():
                raw_payload = data.split("&")
                for raw in raw_payload:
                    payload_data = raw.split("=")
                    payload[payload_data[0]] = payload_data[1]

        return payload
    
    """
    Returns the request cookies
    """
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

    """
    Returns the template route if the route is parsable
    """
    def __get_template_from_parsed_route(self, requested_route, route_list):
        for route, callback in route_list.items():
            parser = mocha_parser.parser(route, requested_route)
            if parser.is_parsable():
                return route
            
        return None

    """
    Returns the callback from the given parsed route
    """
    def __get_callback_from_parsed_route(self, requested_route, route_list):
        for route, callback in route_list.items():
            parser = mocha_parser.parser(route, requested_route)
            if parser.is_parsable():
                return callback
            
        return None

    """
    Writes the full HTTP response to the client
    """
    def __write_full_response(self, response):
        self.connection.sendall(response.header.encode())
        self.connection.sendall(str("\r\n").encode())
        self.connection.sendall(response.body.encode())