from smile import Smile, HTMLResponse, Request

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


@app.route("/required_args")
async def required_args(number: int, string: str):
    return {"number": number, "string": string}


@app.route("/optional_args")
async def optional_args(number: int = 0, string: str = ""):
    return {"number": number, "string": string}


@app.route("/exception")
async def exception():
    return str(1 / 0)


@app.route("/request_arg")
async def request_arg(request: Request):
    return {
        "request.url": {"path": request.url.path, "query_args": request.url.query_args},
        "request.headers": request.headers,
    }


@app.route("/kwargs")
async def kwargs_response(**kwargs):
    return {"kwargs": kwargs}


app.add_error_handler(404, lambda: ("404 Not Found! (Custom error handler)", 404))
app.add_error_handler(
    500, lambda: ("500 Internal Server Error! (Custom error handler)", 404)
)


if __name__ == "__main__":
    from uvicorn import run

    run(app)
