import os
from dotenv import load_dotenv

# .env 파일이 존재하는 경우 환경 변수를 자동으로 로드합니다.
load_dotenv()

# NAVER PAPAGO API Credentials
# 반드시 환경 변수(.env)로 주입해야 합니다. 미설정 시 번역(역번역 교정) 기능은 비활성화되고 원문이 그대로 반환됩니다.
CLIENT_ID = os.getenv("PAPAGO_CLIENT_ID")
CLIENT_SECRET = os.getenv("PAPAGO_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    print("[Warning] PAPAGO_CLIENT_ID / PAPAGO_CLIENT_SECRET 미설정 — 역번역 교정 기능이 비활성화됩니다.")
PAPAGO_URL = "https://openapi.naver.com/v1/papago/n2mt"

# Model Paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
SIMILARITY_MODEL_PATH = os.path.join(MODEL_DIR, "KoBERT_similarity")
HOMONYM_DOBOK_MODEL_PATH = os.path.join(MODEL_DIR, "KoBERT_homonym_dobok")
HOMONYM_HWA_MODEL_PATH = os.path.join(MODEL_DIR, "KoBERT_homonym_hwa")
HOMONYM_DOJANG_MODEL_PATH = os.path.join(MODEL_DIR, "KoBERT_homonym_dojang")

# Data Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DICTIONARY_PATH = os.path.join(DATA_DIR, "agriculture_dictionary.xlsx")
