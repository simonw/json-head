from sanic import Sanic
from sanic import response
import aiohttp
import asyncio
import re
import json

app = Sanic(__name__)

INDEX = """<!DOCTYPE html>
<title>json-head</title>
<h1>json-head</h1>
<p>JSON (and JSON-P) API for running HEAD requests against one or more URLs.
<ul>
    <li><a href="/?url=http://www.google.com/">/?url=http://www.google.com/</a>
    <li><a href="/?url=http://www.yahoo.com/&amp;callback=foo">/?url=http://www.yahoo.com/&amp;callback=foo</a>
    <li><a href="/?url=https://www.google.com/&amp;url=http://www.yahoo.com/">/?url=https://www.google.com/&amp;url=http://www.yahoo.com/</a>
</ul>
<p>Background: <a href="https://simonwillison.net/2017/Oct/14/async-python-sanic-now/">Deploying an asynchronous Python microservice with Sanic and Zeit Now</a></p>
<p>Source code: <a href="https://github.com/simonw/json-head">github.com/simonw/json-head</a></p>
"""

callback_re = re.compile(r'^[a-zA-Z_](\.?[a-zA-Z0-9_]+)+$')
is_valid_callback = callback_re.match


async def head(session, url):
    try:
        async with session.head(url) as response:
            return {
                'ok': True,
                'headers': dict(response.headers),
                'status': response.status,
                'url': url,
            }
    except Exception as e:
        return {
            'ok': False,
            'error': str(e),
            'url': url,
        }


@app.route('/')
async def handle_request(request):
    urls = request.args.getlist('url')
    callback = request.args.get('callback')
    if urls:
        if len(urls) > 10:
            return response.json([{
                'ok': False,
                'error': 'Max 10 URLs allowed'
            }], status=400)
        async with aiohttp.ClientSession() as session:
            head_infos = await asyncio.gather(*[
                head(session, url) for url in urls
            ])
            if callback and is_valid_callback(callback):
                return response.text(
                    '{}({})'.format(callback, json.dumps(head_infos, indent=2)),
                    content_type='application/javascript',
                    headers={'Access-Control-Allow-Origin': '*'},
                )
            else:
                return response.json(
                    head_infos,
                    headers={'Access-Control-Allow-Origin': '*'},
                )
    else:
        return response.html(INDEX)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8006)
