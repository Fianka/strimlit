from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests
from pymongo import MongoClient

# Setup Chrome
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Akses halaman
driver.get("https://flo.health/health-library")
time.sleep(5)

# Scroll untuk muat semua artikel
for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# Ambil isi HTML
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# Cari semua link artikel
links = []
for a in soup.find_all('a', href=True):
    href = a['href']
    if href.startswith('/') and '/health-library/' not in href:
        full = "https://flo.health" + href
        links.append(full)

# Buang duplikat
links = list(set(links))

# Setup MongoDB
client = MongoClient('mongodb+srv://fianka:finn@cluster0.sbuemvv.mongodb.net/flo_helath?retryWrites=true&w=majority')
db = client.flo_health
collection = db.articles

# Ambil konten tiap artikel
def get_content(url):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        title = soup.find('h1').get_text(strip=True)
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text(strip=True) for p in paragraphs])
        return {"url": url, "title": title, "content": content}
    except:
        return None

# Simpan ke MongoDB
for link in links[:100]:
    article = get_content(link)
    if article and not collection.find_one({"url": article["url"]}):
        collection.insert_one(article)
        print(f"Saved: {article['title']}")