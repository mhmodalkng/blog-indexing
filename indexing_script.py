from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import xml.etree.ElementTree as ET

# إعدادات الحساب وصلاحيات API
SCOPES = ['https://www.googleapis.com/auth/indexing']
SERVICE_ACCOUNT_FILE = 'service_account.json'  # ملف JSON لحساب الخدمة لديك

# تهيئة حساب الخدمة
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('indexing', 'v3', credentials=credentials)

# دالة لجلب روابط المقالات من ملف sitemap.xml
def get_urls_from_sitemap(sitemap_url):
    resp = requests.get(sitemap_url)
    urls = []
    if resp.status_code == 200:
        root = ET.fromstring(resp.content)
        # اسم مساحة XML الخاصة بالخرائط
        namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        for url in root.findall(f'{namespace}url'):
            loc = url.find(f'{namespace}loc').text
            urls.append(loc)
    else:
        print(f"Failed to fetch sitemap: HTTP {resp.status_code}")
    return urls

# رابط ملف sitemap الخاص بموقعك
SITEMAP_URL = 'https://vlogars.blogspot.com/sitemap.xml'

# جلب روابط المقالات
urls = get_urls_from_sitemap(SITEMAP_URL)

# دالة لإرسال رابط للفهرسة عبر API
def publish_url(url):
    try:
        body = {
            "url": url,
            "type": "URL_UPDATED"  # نوع الحدث URL_UPDATED يعني تم تحديث الرابط أو جديد
        }
        response = service.urlNotifications().publish(body=body).execute()
        print(f"Sent for indexing: {url}")
    except Exception as e:
        print(f"Error sending {url}: {e}")

# إرسال كل الروابط في ملف sitemap إلى جوجل
for url in urls:
    publish_url(url)
