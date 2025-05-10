import asyncio
import aiohttp
from bs4 import BeautifulSoup
import requests

rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

async def fetch_book(session, book_url):
    try:
        async with session.get(book_url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.select_one('h1').get_text(strip=True)
            price = soup.select_one('p.price_color').get_text(strip=True)
            rating_class = soup.select_one('p.star-rating')['class'][1]
            rating = rating_map.get(rating_class, "N/A")

            category = soup.select('ul.breadcrumb li a')
            category_name = category[-1].get_text(strip=True) if category else "Неизвестно"

            return {
                'title': title,
                'price': price,
                'rating': rating,
                'category': category_name
            }
    except Exception as e:
        print(f"Ошибка при парсинге {book_url}: {e}")
        return None

async def parse_books_async(book_urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_book(session, url) for url in book_urls]
        books = await asyncio.gather(*tasks)
        return [book for book in books if book is not None]

def parse_page(base_url):
    all_books = []
    page_num = 1
    url = base_url

    while url:
        print(f"Парсинг страницы {page_num}: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        if page_num == 1:
            title = soup.title.string.strip() if soup.title else "Заголовок не найден"


        book_links = [a['href'] for a in soup.select('article.product_pod h3 a')]
        full_book_links = [requests.compat.urljoin(url, link) for link in book_links]

        
        books_on_page = asyncio.run(parse_books_async(full_book_links))
        all_books.extend(books_on_page)

        
        next_btn = soup.select_one('li.next > a')
        if next_btn:
            url = requests.compat.urljoin(url, next_btn['href'])
            page_num += 1
        else:
            url = None

    
    with open("output.txt", "w", encoding="utf-8-sig") as f:
        f.write(f"Заголовок: {title}\n\n")
        f.write("Книги на всех страницах:\n")
        for book in all_books:
            f.write(
                f"- {book['title']}\n"
                f"  Цена: {book['price']}\n"
                f"  Рейтинг: {book['rating']}/5\n"
                f"  Категория: {book['category']}\n\n"
            )
    print(f"Готово! Сохранено {len(all_books)} книг в output.txt")

if __name__ == "__main__":
    url = input("Введите URL для парсинга: ")
    parse_page(url)

