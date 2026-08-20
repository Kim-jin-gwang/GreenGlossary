import os

# Model Paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
SIMILARITY_MODEL_PATH = os.path.join(MODEL_DIR, "KoBERT_similarity")
HOMONYM_DOBOK_MODEL_PATH = os.path.join(MODEL_DIR, "KoBERT_homonym_dobok")
HOMONYM_HWA_MODEL_PATH = os.path.join(MODEL_DIR, "KoBERT_homonym_hwa")
HOMONYM_DOJANG_MODEL_PATH = os.path.join(MODEL_DIR, "KoBERT_homonym_dojang")

# Data Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DICTIONARY_PATH = os.path.join(DATA_DIR, "agriculture_dictionary.xlsx")
