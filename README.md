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

### Roadmap.

- [x] ASGI app
- [x] Route && decorators.
- [x] Params (with special internal types).
- [x] Error handlers (for code).
- [] Exception error handlers.
- [] Rework routing system with more advanced solution.
- [] Body data fetching.
- [] Middlewares
- [] Templating engine? (Jinja?)
- [] Allow to set route allowed methods.

### Running with Uvicorn

```python
import uvicorn
from app.app import app

uvicorn.run(app, port=8000)
```
