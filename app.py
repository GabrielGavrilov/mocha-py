import mocha

app = mocha.mocha()

app.set("views", "views/")
app.set("static", "public/")

@app.get("/")
def index(req, res):
    res.initialize_header("200 OK", "text/html")
    res.send(f"Cookie: {req.cookie.get('firstName')}")

@app.get("*")
def not_found(req, res):
    res.initialize_header("200 OK", "text/html")
    res.send("Not found.")

app.listen(3000)