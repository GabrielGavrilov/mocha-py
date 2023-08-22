import mocha

app = mocha.mocha()

app.set("views", "views/")
app.set("static", "public/")

@app.get("/")
def index(req, res):
    res.initialize_header("200 OK", "text/html")
    res.render("index.html")

@app.get("/{greeting}/{name}")
def greet(req, res):
    res.initialize_header("200 OK", "text/html")
    res.send(req.parameter.get("greeting") + " " + req.parameter.get("name"))

@app.get("/about")
def about(req, res):
    res.initialize_header("200 OK", "text/html")
    res.render("about.html")

@app.post("/submit")
def submit(req, res):
    res.initialize_header("200 OK", "text/html")
    print(req.header)
    res.send(f"{req.payload.get('first_name_input')} {req.payload.get('last_name_input')}")

app.listen(8080)