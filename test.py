from smile import Smile, HTMLResponse


app = Smile()


@app.route("/test")
async def test_route():
    return HTMLResponse("<h1>Hello world!</h1>", 200)


if __name__ == "__main__":
    from uvicorn import run

    run(app)
