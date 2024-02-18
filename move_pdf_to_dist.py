import os
import shutil


def main():
    directory = '.'
    target_directory = 'books'
    # 遍历目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_source_path = os.path.join(root, file)
                pdf_target_path = os.path.join(target_directory, file)
                shutil.copy(pdf_source_path, pdf_target_path)
                print(pdf_source_path)


if __name__ == '__main__':
    main()
