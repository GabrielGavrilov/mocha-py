import mocha

app = mocha.mocha()

app.set("views", "views/")
app.set("static", "public/")

@app.get("/")
def index(req, res):
    res.initialize_header("200 OK", "text/html")
    res.render("about.html")

@app.post("/todo")
def todo(req, res):
    res.initialize_header("200 OK", "application/json")
    print(req.payload.get("todoInput"))
    res.send("{\"status\": \"success\"}")

app.listen(3000, "0.0.0.0")