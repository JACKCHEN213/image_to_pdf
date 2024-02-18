# -*- coding: utf8 -*-
import re
import json
import os.path
import urllib.parse

from aiohttp import InvalidURL
import asyncio
from pathlib import Path

import aiohttp
from aiofile import async_open


def load_js(filename):
    with open(filename, 'r', encoding='utf8') as fp:
        return fp.read()


def load_folder_data(filename):
    with open(filename, 'r', encoding='utf8') as fp:
        return json.load(fp)


async def save_to_json(js_content, filename):
    json_content = re.findall(r'^[^{]*([\s\S]*);', js_content)[0]
    try:
        data = json.loads(json_content)
        if data.get('fliphtml5_pages') is not None:
            content = {
                'images': data['fliphtml5_pages']
            }
            async with async_open(filename, 'w', encoding='utf8') as fp:
                print('保存文件: {}'.format(filename))
                json_data = json.dumps(content, indent=2, ensure_ascii=False)
                await fp.write(json_data)
    except json.decoder.JSONDecodeError:
        pass


async def request_url(session, url, filename):
    async with session.get(url) as response:
        return {'filename': filename, 'file_content': await response.text()}


async def save_book_image_url(folder_name: Path, folder, session):
    tasks = []
    for book in folder.get('books', []):
        book_name = book['title']
        b_link = book['bLink']
        book_path = folder_name / book_name
        if not book_path.exists():
            book_path.mkdir(parents=True, exist_ok=True)
        filename = book_path / 'source.json'
        tasks.append(request_url(session, book_url_format.format(b_link), filename.__str__()))
        books.append({
            'name': book_name,
            'type': folder['title'],
            'image_path': filename.__str__(),
            'output_path': (book_path / 'output').__str__(),
            'middle_path': '/tlbo/' + b_link,
        })
    data = await asyncio.gather(*tasks)
    await asyncio.gather(*[save_to_json(item['file_content'], item['filename']) for item in data])


async def main():
    folder_data = load_folder_data('folders.json')
    conn = aiohttp.TCPConnector(limit=15)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = []
        for folder in folder_data:
            folder_name = Path(folder['title'])
            if not folder_name.exists():
                folder_name.mkdir(parents=True, exist_ok=True)
            tasks.append(save_book_image_url(folder_name, folder, session))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    book_url_format = 'https://book.yunzhan365.com/tlbo/{}/mobile/javascript/config.js'
    books = []
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    with open('books.json', 'w', encoding='utf8') as f:
        print('保存books.json')
        json.dump(books, f, indent=2, ensure_ascii=False)
