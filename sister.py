# (S)I(S)TE(R)
# CraftJobs SSR

import quart
import asyncio
import json
from http3 import AsyncClient
from hypercorn.asyncio import serve, Config

app = quart.Quart(__name__)
http = AsyncClient()
app_config = None


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def handle(path: str):
    embeds = ""

    text: str = ''

    with open(app_config['index_path'], 'r') as f:
        text = f.read()

    if path.startswith('i/') or path == '':
        pass
    else:
        resp = await http.get(app_config['api'] + '/users/' + path)
        raw = await resp.read()
        j = resp.json()

        success = j['success']

        embeds += title('@' + j['user']['username'] if success
                        else 'User not found')
        embeds += meta('og:description',
                       '@' + j['user']['username'] + ' is on CraftJobs!'
                       if success else 'CraftJobs')
        text = text.replace('"sister-preload"', raw.decode('utf-8'))

        if success:
            print(j['user'])
            embeds += meta('og:image', j['user']['avatarUrl'])

    embeds += meta('og:url', 'https://craftjobs.net/' + path)
    embeds += meta('theme-color', '#FFAAFF')

    text = text.replace('<sister-embeds></sister-embeds>', embeds)
    return text


def meta(prop: str, content: str) -> str:
    return f'<meta content="{prop}" property="{content}">\n'


def title(name: str) -> str:
    return meta('og:title', name) + f'\n<title>{name}</title>'


if __name__ == '__main__':
    with open('config.json', 'r') as file:
        app_config = json.load(file)

    config = Config()
    config.bind = 'localhost:7086'
    asyncio.run(serve(app, config))