from bs4 import BeautifulSoup
import requests
import os
from ebooklib import epub
import re
import pathlib

# insert here chapters, which you want to parse
start_chapter = 1001
end_chapter = 1003


def get_html(url):
    r = requests.get(url)
    return r.text


def delete_old_files():
    for (dirpath, dirnames, filenames) in os.walk('.\\files_for_epub'):
        for filename in filenames:
            if filename.startswith('Chapter'):
                path_to_filename = os.getcwd() + '.\\files_for_epub\\' + filename
                os.remove(path_to_filename)


def get_page_data(html):
    # parse text to files
    soup = BeautifulSoup(html, 'lxml')
    chapter = soup.find('div', id='chapter-content')
    chapter_name = soup.find('a', class_='chapter-title').get('title')
    file_name = re.search(r'Chapter \d+', chapter_name).group(0)
    with open('.\\files_for_epub\\' + file_name + '.xhtml', "w", encoding='utf-8') as file:
        file.write(str(chapter))


def edit_files():
    # removes ad blocks and last line
    for (dirpath, dirnames, filenames) in os.walk('.\\files_for_epub'):
        for filename in filenames:
            path = os.getcwd() + '.\\files_for_epub\\' + filename
            with open(path, encoding='utf-8') as f:
                text = f.read()
                newtext_iter1 = re.sub(r'<script.+?</script>', '', text, flags=re.MULTILINE)
                newtext_iter2 = re.sub(r'<ins.+?</ins>', '', newtext_iter1, flags=re.MULTILINE)
                newtext_iter3 = re.sub(r'<script>\n\n.+?\n\n</script>', '', newtext_iter2, flags=re.MULTILINE)
                finalnewtext = re.sub(r'If you find any errors.+?as possible.', '', newtext_iter3)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(finalnewtext)


def create_epub():
    # a bit of epub magic
    book = epub.EpubBook()
    book.set_identifier(f'{start_chapter}-{end_chapter}')
    book.set_title(f'Release that Witch. Chapters {start_chapter}-{end_chapter}')
    book.set_language('en')

    book.spine = ['nav']
    for (dirpath, dirnames, filenames) in os.walk('.\\files_for_epub'):
        for filename in filenames:
            filename_short = filename.split('.')[0]
            f = open('.\\files_for_epub\\' + filename_short + '.xhtml', encoding='utf-8')
            text = f.read()
            f.close()
            c1 = epub.EpubHtml(title=filename_short, file_name=filename, lang='en')
            c1.content = text
            book.add_item(c1)
            book.toc.append(c1)
            book.spine.append(c1)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(f'Release that Witch. Chapters {start_chapter}-{end_chapter}.epub', book, {})


def main():
    # example_url = "http://novelfull.com/release-that-witch/chapter-1200.html"
    base_url = "http://novelfull.com/release-that-witch/chapter-"
    ending = ".html"

    pathlib.Path('.\\files_for_epub').mkdir(parents=True, exist_ok=True)  # create directory if not exists
    delete_old_files()
    for i in range(start_chapter, end_chapter + 1):  # parsing cycle
        url_gen = base_url + str(i) + ending
        html = get_html(url_gen)
        get_page_data(html)
    edit_files()

    create_epub()


if __name__ == '__main__':
    main()
