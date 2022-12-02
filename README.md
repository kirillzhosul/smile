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

### Running with Uvicorn

```python
import uvicorn
from app.app import app

uvicorn.run(app, port=8000)
```
