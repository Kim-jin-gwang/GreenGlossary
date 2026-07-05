from flask import Flask, render_template, request
from src.dictionary import AgricultureDictionary
from src.models import ModelManager
from src.nlp_processor import NLPProcessor

app = Flask(__name__)

# 대용량 모델 로드로 인한 시작 지연 방지를 위해 lazy initialization 패턴 적용
model_manager = None
dictionary = AgricultureDictionary()
nlp_processor = NLPProcessor()

def get_model_manager():
    global model_manager
    if model_manager is None:
        model_manager = ModelManager()
        nlp_processor.set_model_manager(model_manager)
    return model_manager

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/result', methods=['POST'])
def process_text():
    text_original = request.form.get('news_original', '').strip()
    if not text_original:
        return render_template('home.html', error="텍스트를 입력해 주세요.")

    # 1. 모델 매니저 로드 (첫 호출 시 초기화)
    manager = get_model_manager()

    # 2. 사전 및 동음이의어 사전 구조 초기화
    jargon_dict = dictionary.get_jargon_dict()
    homonym_dict = dictionary.get_homonym_dict()

    # 3. 사전 매칭 진행
    matched_dict, use_jargon_list, mor_sentences = nlp_processor.match_dictionary(
        text_original, jargon_dict, homonym_dict
    )
    print(f'[INFO] Dictionary Matching Complete. Matched: {use_jargon_list}')

    # 4. 전문용어 치환 (동음이의어 검증 포함)
    std_news, mean_news, replaced_rows = nlp_processor.replace_jargon(
        mor_sentences, matched_dict, use_jargon_list, homonym_dict
    )
    print(f'[INFO] Jargon Replacement Complete. Replaced rows: {replaced_rows}')

    # 5. 역번역 및 문장 유사도 비교를 통해 최적의 텍스트 선택
    result_text = nlp_processor.select_and_translate_news(std_news, mean_news, replaced_rows)
    print('[INFO] Translation & Similarity Selection Complete.')

    return render_template('after.html', result=result_text, original=text_original)

if __name__ == "__main__":
    # 서버 기동 시 모델 pre-loading 수행
    print("[INFO] Pre-initializing models on startup...")
    get_model_manager()
    app.run(debug=True, host="127.0.0.1", port=5000)
