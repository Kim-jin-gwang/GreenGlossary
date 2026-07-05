import os
from dotenv import load_dotenv

# .env 파일이 존재하는 경우 환경 변수를 자동으로 로드합니다.
load_dotenv()

# NAVER PAPAGO API Credentials
# 환경 변수 사용을 권장하며, 없을 경우 기존 하드코딩된 API Key를 기본값으로 사용합니다.
CLIENT_ID = os.getenv("PAPAGO_CLIENT_ID", "Jpd1bwBBSNA6M1AjmPqz")
CLIENT_SECRET = os.getenv("PAPAGO_CLIENT_SECRET", "VlUL02B5qn")
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
