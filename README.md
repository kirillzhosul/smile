# Smile
Python ASGI framework written as educational project.

### Example

```python

from smile import Smile, HTMLResponse

app = Smile()


@app.route("/test")
async def test_route():
    return HTMLResponse("<h1>Hello world!</h1>", 200)

```
