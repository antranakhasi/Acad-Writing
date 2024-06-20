import requests
from bs4 import BeautifulSoup
import docx2txt
import os
from dotenv import load_dotenv

load_dotenv()

LOGIN_URL = os.getenv("ECONOMIST_LOGIN_URL")
USERNAME = os.getenv("ECONOMIST_USERNAME")
PASSWORD = os.getenv("ECONOMIST_PASSWORD")

def extract_text_from_docx(file):
    return docx2txt.process(file)

def extract_article(session, url):
    article_page = session.get(url)
    if article_page.status_code == 200:
        soup = BeautifulSoup(article_page.content, 'html.parser')

        for elem in soup.find_all(['script', 'style', 'noscript', 'iframe']):
            elem.extract()

        article = soup.find('article')  # adjust as per the structure of the HTML

        if article:
            article_text = article.get_text(separator='\n')
            return article_text.strip()
        else:
            return "Article content not found."
    else:
        raise Exception(f"Failed to fetch article, status code: {article_page.status_code}")

def login_and_get_article(target_url):
    with requests.Session() as session:
 
        login_page = session.get(LOGIN_URL)
        login_page_soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = login_page_soup.find("input", {"name": "csrf_token"}).get("value")

 
        payload = {
            "username": USERNAME,
            "password": PASSWORD,
            "csrf_token": csrf_token
        }
        login_response = session.post(LOGIN_URL, data=payload)

        if login_response.status_code == 200:
            article_text = extract_article(session, target_url)
            return article_text
        else:
            raise Exception(f"Login failed, status code: {login_response.status_code}")