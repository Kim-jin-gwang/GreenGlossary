import numpy as np
import tensorflow as tf
import tensorflow_text  # KoBERT 구동 시 필요
from config import (
    SIMILARITY_MODEL_PATH,
    HOMONYM_DOBOK_MODEL_PATH,
    HOMONYM_HWA_MODEL_PATH,
    HOMONYM_DOJANG_MODEL_PATH
)

class ModelManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        
        print("[INFO] Loading TensorFlow Keras models...")
        try:
            self.similarity_model = tf.keras.models.load_model(SIMILARITY_MODEL_PATH)
            self.homonym_dobok = tf.keras.models.load_model(HOMONYM_DOBOK_MODEL_PATH)
            self.homonym_hwa = tf.keras.models.load_model(HOMONYM_HWA_MODEL_PATH)
            self.homonym_dojang = tf.keras.models.load_model(HOMONYM_DOJANG_MODEL_PATH)
            
            self.homonym_models = {
                '도복': self.homonym_dobok,
                '화형': self.homonym_hwa,
                '도장': self.homonym_dojang
            }
            self._initialized = True
            print("[INFO] All models loaded successfully.")
        except Exception as e:
            print(f"[Error] Failed to load models: {e}")
            raise e

    def calculate_similarity(self, sentences1, sentences2):
        """
        두 문장 리스트 간의 문장 유사도 벡터를 계산합니다.
        """
        if isinstance(sentences1, str):
            sentences1 = [sentences1]
        if isinstance(sentences2, str):
            sentences2 = [sentences2]
            
        tensor1 = tf.constant(sentences1)
        tensor2 = tf.constant(sentences2)

        embeddings1 = self.similarity_model(tensor1)
        embeddings2 = self.similarity_model(tensor2)
        
        result = tf.tensordot(embeddings1, embeddings2, axes=[[1], [1]]).numpy()
        return np.diag(result)

    def check_homonym(self, jargon, spacing_sentence):
        """
        동음이의어 모델을 사용해 문맥상 올바른 전문용어로 사용되었는지 검증합니다.
        """
        model = self.homonym_models.get(jargon)
        if not model:
            return True
            
        prediction = model.predict([spacing_sentence])
        return bool(prediction >= 0.8)
