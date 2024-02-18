import json

from PIL import Image
from reportlab.pdfgen import canvas
from pathlib import Path
import threading


class ExportPDFThread(threading.Thread):
    def __init__(self, book_path, image_path):
        threading.Thread.__init__(self)
        self.book_path = book_path
        self.image_path = image_path

    def run(self) -> None:
        save_to_pdf(self.book_path, get_image_paths(self.image_path))


def save_to_pdf(filename, image_paths):
    c = canvas.Canvas(filename.__str__())

    index = 1
    for image in image_paths:
        img = Image.open(image)
        # 这里我们假设所有图像大小相同
        c.setPageSize((img.width, img.height))
        c.drawInlineImage(img, 0, 0, width=img.width, height=img.height)
        c.showPage()  # 结束当前页并创建一个新页
        # print('处理图片{}'.format(index))
        index += 1

    c.save()  # 保存PDF
    print('完成pdf保存: {}'.format(filename))


def get_image_paths(path: Path):
    for filepath in path.glob('*'):
        if filepath.is_file():
            yield filepath


def export_to_pdf(book_path, image_path):
    save_to_pdf(book_path, get_image_paths(image_path))


def load_book_data(file_name):
    with open(file_name, 'r', encoding='utf8') as fp:
        return json.load(fp)


def main():
    threads = []
    for book in load_book_data('books.json'):
        threads.append(ExportPDFThread(
            Path(book['output_path']) / (book['name'] + '.pdf'),
            Path(book['output_path']) / 'images')
        )

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
