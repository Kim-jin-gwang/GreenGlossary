import pandas as pd
from config import DICTIONARY_PATH

class AgricultureDictionary:
    def __init__(self, file_path=DICTIONARY_PATH):
        self.file_path = file_path
        self.df = None
        self.jargon_dict = {}
        self.homonym_dict = {'도복': [], '화형': [], '도장': []}
        self.load_dictionary()

    def load_dictionary(self):
        try:
            self.df = pd.read_excel(self.file_path)
            # 공백 문자 정제
            for col in ['jargon_name', 'std_name', 'mean_s']:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str).str.replace(r'\xa0', ' ', regex=True).str.strip()

            # jargon_dict 매핑 테이블 구축
            for _, row in self.df.iterrows():
                self.jargon_dict[row['jargon_name']] = [row['std_name'], row['mean_s']]
        except Exception as e:
            print(f"[Error] Failed to load dictionary file: {e}")

    def get_jargon_dict(self):
        return self.jargon_dict

    def get_homonym_dict(self):
        return {key: [] for key in self.homonym_dict}
