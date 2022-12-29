from smile import Smile
import jinja2

app = Smile()


@app.route("/jinja")
async def jinja_template(app: Smile):
    return await app.jinja_template("test.jinja"), 200


app.setup_jinja_environment(
    jinja2.Environment(enable_async=True, loader=jinja2.FileSystemLoader("templates"))
)

if __name__ == "__main__":
    from uvicorn import run

    run(app)
