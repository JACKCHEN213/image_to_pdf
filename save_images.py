# -*- coding: utf8 -*-
import json
import os.path
import urllib.parse

from aiohttp import InvalidURL
import asyncio
from pathlib import Path

import aiohttp
from aiofile import async_open


async def download_images(session, url, file_name: Path):
    try:
        async with session.get(url) as response:
            await save_image(file_name, response)
    except InvalidURL:
        pass


async def save_image(path: Path, response):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    async with async_open(path, 'wb') as fp:
        print('保存图片: {}'.format(path.__str__()))
        await fp.write(
            await response.read()
        )


def load_image_data(file_name):
    with open(file_name, 'r', encoding='utf8') as fp:
        data = json.load(fp)
        return data['images']


def get_file_extension(url):
    parse_url = urllib.parse.urlparse(url)
    path = parse_url.path
    return os.path.splitext(path)[1]


def get_request_url(url, middle_path):
    return urllib.parse.urljoin(base_url, middle_path + url.replace('..', ''))


def get_save_name(i, extension, output_path):
    return output_path / '{:04}{}'.format(i + 1, extension)


async def process_image(image_path, output_path, middle_path):
    images = load_image_data(image_path)
    conn = aiohttp.TCPConnector(limit=15)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = []
        for k, v in enumerate(images):
            for url in v['n']:
                extension = get_file_extension(url)
                tasks.append(download_images(session, get_request_url(url, middle_path),
                                             get_save_name(k, extension, output_path)))
        await asyncio.gather(*tasks)


def load_book_data(file_name):
    with open(file_name, 'r', encoding='utf8') as fp:
        return json.load(fp)


async def main():
    tasks = []
    for book in load_book_data('books.json'):
        tasks.append(process_image(
            book['image_path'],
            Path(book['output_path']) / 'images',
            book['middle_path']
        ))
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    base_url = 'https://book.yunzhan365.com'
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
