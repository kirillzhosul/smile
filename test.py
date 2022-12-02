from smile import Smile, HTMLResponse


app = Smile()


@app.route("/html")
async def html_response():
    return HTMLResponse("<h1>Hello world!</h1>", 200)


@app.route("/plain")
async def plain_response():
    return "Hello world!"


@app.route("/tuple")
async def tuple_response():
    return "Hello world!", 200


@app.route("/json")
async def json_response():
    # Also allowed as tuple.
    return {"key": "field", "number": 1}


if __name__ == "__main__":
    from uvicorn import run

    run(app)
