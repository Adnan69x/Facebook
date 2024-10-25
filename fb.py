import requests
import re
import json
from http.cookiejar import MozillaCookieJar
from requests.utils import cookiejar_from_dict

def generate_id(url):
    match = re.search(r'(\d+)/?$', url)
    return match.group(1) if match else None

def clean_str(string):
    return json.loads(f'{{"text": "{string}"}}')["text"]

def get_sd_link(content):
    match = re.search(r'browser_native_sd_url":"([^"]+)"', content)
    return clean_str(match.group(1)) if match else None

def get_hd_link(content):
    match = re.search(r'browser_native_hd_url":"([^"]+)"', content)
    return clean_str(match.group(1)) if match else None

def get_title(content):
    match = re.search(r'<title>(.*?)<\/title>', content) or re.search(r'title id="pageTitle">(.+?)<\/title>', content)
    return clean_str(match.group(1)) if match else None

def fetch_facebook_data(url, cookies_file_path):
    headers = {
        'sec-fetch-user': '?1',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-site': 'none',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'cache-control': 'max-age=0',
        'authority': 'www.facebook.com',
        'upgrade-insecure-requests': '1',
        'accept-language': 'en-GB,en;q=0.9,tr-TR;q=0.8,tr;q=0.7,en-US;q=0.6',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    
    # Load cookies from Netscape format cookies.txt
    cookie_jar = MozillaCookieJar()
    cookie_jar.load(cookies_file_path, ignore_discard=True, ignore_expires=True)
    
    try:
        response = requests.get(url, headers=headers, cookies=cookie_jar, timeout=10, verify=False)
        response.raise_for_status()
        data = response.text
        
        result = {
            "success": True,
            "id": generate_id(url),
            "title": get_title(data),
            "links": {}
        }
        
        if sd_link := get_sd_link(data):
            result["links"]["Download Low Quality"] = f"{sd_link}&dl=1"
        
        if hd_link := get_hd_link(data):
            result["links"]["Download High Quality"] = f"{hd_link}&dl=1"
            
    except requests.RequestException as e:
        result = {"success": False, "message": str(e)}

    return json.dumps(result, indent=4)

# Example usage
cookies_file_path = 'cookies.txt'
url = "https://www.facebook.com/share/r/M8CKfp7nFyMw4j2X/"
print(fetch_facebook_data(url, cookies_file_path))
