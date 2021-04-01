# (S)I(S)TE(R)
# CraftJobs SSR

import quart
import asyncio
import json
from http3 import AsyncClient
from hypercorn.asyncio import serve, Config

app = quart.Quart(__name__)
app_config = None


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def handle(path: str):
    request: quart.Request = quart.request
    embeds = ""

    with open(app_config['index_path'], 'r') as f:
        text: str = f.read()

    try:
        if path.startswith('i/') or path == '':
            pass
        else:
            async with AsyncClient() as http:
                headers = {}

                if 'sistoken' in request.cookies:
                    headers['Authorization'] = request.cookies.get('sistoken')

                resp = await http.get(app_config['api'] + '/users/' + path,
                                      headers=headers)
            j = resp.json()

            success = j['success']

            embeds += title('@' + j['user']['username'] if success
                            else 'User not found')
            embeds += meta('og:description',
                           '@' + j['user']['username'] + ' is on CraftJobs!'
                           if success else 'CraftJobs')

            j['target'] = path.lower()

            text = text.replace('"sister-preload"', json.dumps(j))

            if success:
                embeds += meta('og:image', j['user']['avatarUrl'])

        embeds += meta('og:url', 'https://craftjobs.net/' + path)
        embeds += meta('theme-color', '#FFAAFF')

        text = text.replace('<sister-embeds></sister-embeds>', embeds)
        return text
    # Panic mode to stop 500s
    except Exception as e:
        print(e)
        return text


def meta(prop: str, content: str) -> str:
    return f'<meta content="{content}" property="{prop}">\n'


def title(name: str) -> str:
    return meta('og:title', name) + f'\n<title>{name}</title>'


if __name__ == '__main__':
    with open('config.json', 'r') as file:
        app_config = json.load(file)

    config = Config()
    config.bind = 'localhost:7086'
    asyncio.run(serve(app, config))
