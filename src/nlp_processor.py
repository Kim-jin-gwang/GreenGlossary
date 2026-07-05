import copy
import re
from konlpy.tag import Okt
from src.translator import reverse_trans

class NLPProcessor:
    def __init__(self, model_manager=None):
        self.okt = Okt()
        self.model_manager = model_manager

    def set_model_manager(self, model_manager):
        self.model_manager = model_manager

    def restore_spacing(self, pos_tags):
        """
        형태소 분석(okt.pos) 결과 리스트를 받아서 조사를 제외하고 적절하게 공백을 붙여 복원합니다.
        """
        if not pos_tags:
            return ""
        
        corrected = ""
        for word, pos in pos_tags:
            if pos in ('Josa', 'PreEomi', 'Eomi', 'Suffix', 'Punctuation'):
                corrected += word
            else:
                corrected += " " + word
        
        if corrected.startswith(" "):
            corrected = corrected[1:]
        return corrected

    def match_dictionary(self, text_data, jargon_dict, homonym_dict):
        """
        입력 텍스트를 문장 단위로 나누어 전문용어 및 동음이의어 사전과 매칭하고 위치를 기록합니다.
        """
        # 개행 제거 및 문장 단위로 분할
        cleaned_text = re.sub(r"\n+", " ", text_data)
        sentences = re.split(r"[\.?!]\s+", cleaned_text)
        # 빈 문장 제거
        sentences = [s for s in sentences if s.strip()]

        use_jargon = set()
        mor_sentences = []

        for i, sentence in enumerate(sentences):
            pos_tags = self.okt.pos(sentence)
            mor_sentences.append(pos_tags)

            for j, (word, _) in enumerate(pos_tags):
                if word in jargon_dict:
                    # [sentence_idx, token_idx] 위치 기록
                    jargon_dict[word].append([i, j])
                    use_jargon.add(word)

        return jargon_dict, use_jargon, mor_sentences

    def replace_jargon(self, mor_sentences, use_jargon_dict, use_jargon_list, homonym_dict):
        """
        전문용어를 표준어 또는 설명문(의미문)으로 대체합니다.
        동음이의어 후보 단어는 딥러닝 모델을 사용하여 의미를 검증합니다.
        """
        std_news = copy.deepcopy(mor_sentences)
        mean_news = copy.deepcopy(mor_sentences)
        replaced_sentence_rows = set()

        for word in use_jargon_list:
            # use_jargon_dict[word] 구조: [std_name, mean_s, [row1, col1], [row2, col2], ...]
            # 따라서 index 2 이후부터 실제 매칭된 단어의 위치 정보
            for loc_info in use_jargon_dict[word][2:]:
                row, column = loc_info[0], loc_info[1]

                # 동음이의어 검증이 필요한 단어인 경우
                if word in homonym_dict:
                    spacing_sentence = self.restore_spacing(mor_sentences[row])
                    if self.model_manager and self.model_manager.check_homonym(word, spacing_sentence):
                        # 전문용어로 사용된 것이 맞다면 치환
                        self._apply_replacement(std_news, row, column, use_jargon_dict[word][0])
                        self._apply_replacement(mean_news, row, column, use_jargon_dict[word][1])
                        replaced_sentence_rows.add(row)
                else:
                    # 일반 전문용어는 항상 치환
                    self._apply_replacement(std_news, row, column, use_jargon_dict[word][0])
                    self._apply_replacement(mean_news, row, column, use_jargon_dict[word][1])
                    replaced_sentence_rows.add(row)

        return std_news, mean_news, list(replaced_sentence_rows)

    def _apply_replacement(self, news_structure, row, column, new_word):
        # Okt.pos 튜플 구조 (word, pos) 에서 word 값만 새로운 단어로 교체
        pos_tag_list = list(news_structure[row][column])
        pos_tag_list[0] = new_word
        news_structure[row][column] = tuple(pos_tag_list)

    def select_and_translate_news(self, std_news, mean_news, replaced_rows):
        """
        변환된 표준어 및 의미문 문장을 역번역한 후, 문장 유사도를 비교하여 더 자연스러운 결과를 최종 선택합니다.
        """
        std_sentence_news = [self.restore_spacing(s) for s in std_news]
        mean_sentence_news = [self.restore_spacing(m) for m in mean_news]

        final_sentences = copy.deepcopy(std_sentence_news)

        for idx in replaced_rows:
            # 1. 각각의 버전으로 역번역(한-일-한) 수행하여 조사 교정
            papago_std = reverse_trans(std_sentence_news[idx])
            papago_mean = reverse_trans(mean_sentence_news[idx])

            # 2. 역번역된 두 문장의 유사도 비교
            if self.model_manager:
                sim_score = self.model_manager.calculate_similarity([papago_std], [papago_mean])[0]
                # 유사도가 낮으면(0.9 이하) 의미가 훼손되었을 우려가 있으므로 더 설명적인 의미문(mean) 선택
                if sim_score <= 0.90:
                    final_sentences[idx] = papago_mean
                else:
                    final_sentences[idx] = papago_std
            else:
                final_sentences[idx] = papago_std

        # 3. 전체 문장을 하나로 결합하고 최종 문맥 번역 정제
        combined_news = " ".join(final_sentences)
        final_translated_news = reverse_trans(combined_news)
        return final_translated_news
