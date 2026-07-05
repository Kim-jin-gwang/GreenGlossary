import json
import urllib.request
import urllib.parse
from config import CLIENT_ID, CLIENT_SECRET, PAPAGO_URL

def translate(text, src_lang='ko', tar_lang='ja'):
    """
    네이버 파파고 API를 이용하여 텍스트를 번역합니다.
    """
    enc_text = urllib.parse.quote(text)
    data = f"source={src_lang}&target={tar_lang}&text={enc_text}"
    
    request = urllib.request.Request(PAPAGO_URL)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
    
    try:
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        res_code = response.getcode()
        if res_code == 200:
            response_body = response.read()
            decode = json.loads(response_body.decode('utf-8'))
            return decode['message']['result']['translatedText']
        else:
            print(f"[Error] Naver API response code: {res_code}")
            return text
    except Exception as e:
        print(f"[Error] Translation failed: {e}")
        return text

def reverse_trans(sentence):
    """
    조사 교정을 위해 한-일-한 역번역을 수행합니다.
    """
    # 1. 한국어 -> 일본어
    ja_text = translate(sentence, src_lang='ko', tar_lang='ja')
    # 2. 일본어 -> 한국어
    ko_text = translate(ja_text, src_lang='ja', tar_lang='ko')
    return ko_text
