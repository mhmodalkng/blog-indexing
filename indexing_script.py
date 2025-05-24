from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import xml.etree.ElementTree as ET

SCOPES = ['https://www.googleapis.com/auth/indexing']
SERVICE_ACCOUNT_FILE = 'service_account.json'  # اسم ملف حساب الخدمة

# تهيئة حساب الخدمة
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('indexing', 'v3', credentials=credentials)

# رابط ملف sitemap الرئيسي
MAIN_SITEMAP_URL = 'https://vlogars.blogspot.com/sitemap.xml'

def get_sitemap_urls(sitemap_url):
    """جلب روابط ملفات sitemap الفرعية من ملف sitemap الرئيسي"""
    resp = requests.get(sitemap_url)
    sitemaps = []
    if resp.status_code == 200:
        root = ET.fromstring(resp.content)
        namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        # في حال وجود ملفات sitemap فرعية
        for sitemap in root.findall(f'{namespace}sitemap'):
            loc = sitemap.find(f'{namespace}loc').text
            sitemaps.append(loc)
        # لو ما لاقاش ملفات فرعية، نجرب نقرأ روابط مباشرة من الملف نفسه
        if not sitemaps:
            sitemaps.append(sitemap_url)
    else:
        print(f"Failed to fetch sitemap: HTTP {resp.status_code}")
    return sitemaps

def get_urls_from_sitemap(sitemap_url):
    """جلب روابط المقالات من ملف sitemap فرعي"""
    resp = requests.get(sitemap_url)
    urls = []
    if resp.status_code == 200:
        root = ET.fromstring(resp.content)
        namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        for url in root.findall(f'{namespace}url'):
            loc = url.find(f'{namespace}loc').text
            urls.append(loc)
    else:
        print(f"Failed to fetch sitemap: HTTP {resp.status_code} for {sitemap_url}")
    return urls

def publish_url(url):
    """إرسال رابط للفهرسة"""
    try:
        body = {
            "url": url,
            "type": "URL_UPDATED"
        }
        response = service.urlNotifications().publish(body=body).execute()
        print(f"Sent for indexing: {url}")
    except Exception as e:
        print(f"Error sending {url}: {e}")

# 1- جلب جميع روابط ملفات sitemap الفرعية أو الملف الرئيسي نفسه
all_sitemaps = get_sitemap_urls(MAIN_SITEMAP_URL)

# 2- جلب جميع الروابط من كل ملفات sitemap
all_urls = []
for sm in all_sitemaps:
    all_urls.extend(get_urls_from_sitemap(sm))

# 3- إرسال كل الروابط للفهرسة
for url in all_urls:
    publish_url(url)
