"""Gradio API server for the GreenGlossary live demo.

농림 전문용어 순화 파이프라인(사전 매칭 → KoBERT 동음이의어 판별 →
치환 + 조사 교정 → KoBERT 유사도 기반 문장 선택)을 REST API로 노출한다.
커스텀 프론트엔드(demo-gateway/greenglossary/)가 이 API를 호출한다.

로컬 실행: python demo_api.py  (사전에 python download_models.py 로 모델 필요)
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import gradio as gr

try:
    # ZeroGPU Space 기동 요건: @spaces.GPU 함수가 최소 1개 필요.
    # 실제 추론은 CPU에서 실행해 방문자별 ZeroGPU 쿼터를 소비하지 않는다.
    import spaces

    @spaces.GPU
    def _zerogpu_startup_requirement():
        return None
except ImportError:  # 로컬 실행 환경
    pass

from src.dictionary import AgricultureDictionary
from src.models import ModelManager
from src.nlp_processor import NLPProcessor

MAX_CHARS = 2000  # 데모 서버 보호

print("[INFO] Loading dictionary / tokenizer / KoBERT models...")
dictionary = AgricultureDictionary()
nlp_processor = NLPProcessor()
model_manager = ModelManager()
nlp_processor.set_model_manager(model_manager)
print("[INFO] Ready.")


def simplify(text: str):
    """농림 전문용어가 포함된 텍스트를 쉬운 우리말로 순화해 JSON으로 반환."""
    text = (text or "").strip()
    if not text:
        raise gr.Error("변환할 문장을 입력해주세요.")
    text = text[:MAX_CHARS]

    jargon_dict = dictionary.get_jargon_dict()
    homonym_dict = dictionary.get_homonym_dict()

    matched_dict, use_jargon_list, mor_sentences = nlp_processor.match_dictionary(
        text, jargon_dict, homonym_dict
    )
    std_news, mean_news, replaced_rows, replaced_terms = nlp_processor.replace_jargon(
        mor_sentences, matched_dict, use_jargon_list, homonym_dict
    )
    result_text = nlp_processor.select_best_sentences(std_news, mean_news, replaced_rows)

    seen = set()
    terms = []
    for t in replaced_terms:
        if t["jargon"] in seen:
            continue
        seen.add(t["jargon"])
        terms.append({
            "용어": t["jargon"],
            "순화어": t["std"],
            "설명": t["mean"],
            "동음이의어판별": t["homonym_checked"],
        })

    return {"original": text, "result": result_text, "terms": terms}


with gr.Blocks(title="GreenGlossary API") as demo:
    gr.Markdown(
        """
        # 🌱 GreenGlossary — 농림 전문용어 순화 API
        어려운 산림·농업 한자어를 쉬운 우리말로 바꿔줍니다.
        KoBERT가 동음이의어(도장·도복·화형)의 문맥을 판별하고, 치환 문장의 의미 유사도를 검증합니다.

        ✨ **커스텀 데모 페이지**: [demo-gateway.trealight112.workers.dev/greenglossary](https://demo-gateway.trealight112.workers.dev/greenglossary/) ·
        📎 [GitHub](https://github.com/Kim-jin-gwang/GreenGlossary)
        """
    )
    with gr.Row():
        with gr.Column():
            inp = gr.Textbox(
                lines=6,
                label="변환할 문장",
                placeholder="산불 피해목의 도장 여부를 확인한 뒤 간벌을 실시한다.",
            )
            btn = gr.Button("쉬운 우리말로 변환", variant="primary")
        out = gr.JSON(label="변환 결과")
    btn.click(simplify, inputs=inp, outputs=out, api_name="simplify")

if __name__ == "__main__":
    demo.launch()
