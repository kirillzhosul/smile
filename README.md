# Smile

Python ASGI framework written as educational project.

### Installing.

Currently package is not published as it is written as educational project!

### Goal.

As I already said many times, this is educational project, there is no goal to
make something very very unique!

### Example

```python

from smile import Smile, HTMLResponse

app = Smile()

# Also there is
# from smile import Request
# with argument of that type Smile will auto pass it to your route handler!


@app.route("/html")
async def html_route(optional_query_param: int = 0):
    return HTMLResponse("<h1>Hello world!</h1>", 200)

@app.route("/json")
async def json_response(required_query_param: str):
    return {"q": required_query_param}, 404

```

### Roadmap.

- [x] ASGI app
- [x] Route && decorators.
- [x] Params (with special internal types).
- [x] Error handlers (for code).
- [ ] Rework routing system with more advanced solution.
- [ ] Allow to set route allowed methods.
- [ ] Body data fetching.
- [ ] Exception error handlers.
- [ ] Middlewares
- [ ] Refactor code and internal caused responses.
- [ ] Templating engine? (Jinja?)
- [ ] More...

### Running with Uvicorn

```python
import uvicorn
from app.app import app

uvicorn.run(app, port=8000)
```
