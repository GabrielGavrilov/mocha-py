import mocha

app = mocha.mocha()

app.set("views", "views/")
app.set("static", "public/")

@app.get("/")
def index(res):
    res.initialize("200 OK", "text/html")
    res.render("index.html")

@app.get("/about")
def about(res):
    res.initialize("200 OK", "text/html")
    res.render("about.html")

app.listen(3000)