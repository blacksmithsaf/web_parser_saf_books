import requests
from bs4 import BeautifulSoup

def parse_page (url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        
        #Парсинг заголовок страницы
        title = soup.title.string if soup.title else "Заголовок не найден"
        print(f"Заголовок страницы: {title}")
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
     
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(f"Заголовок: {title}")   
print("Данные сохранены в output.txt")

if __name__== "__main__":
  url = input("Введите URL для парсинга:")
  parse_page(url)
  
  