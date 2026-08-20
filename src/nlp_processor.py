import copy
import re
from konlpy.tag import Okt


def has_jongseong(word):
    """단어 마지막 글자의 받침(종성) 유무를 반환합니다."""
    if not word:
        return False
    ch = word[-1]
    if not ('가' <= ch <= '힣'):
        return False
    return (ord(ch) - 0xAC00) % 28 != 0


def ends_with_rieul(word):
    """단어 마지막 글자의 받침이 ㄹ인지 반환합니다. ('으로/로' 교정용)"""
    if not word or not ('가' <= word[-1] <= '힣'):
        return False
    return (ord(word[-1]) - 0xAC00) % 28 == 8


# (받침 있을 때, 받침 없을 때) 형태의 조사 쌍
JOSA_BY_JONGSEONG = {
    '을': ('을', '를'), '를': ('을', '를'),
    '이': ('이', '가'), '가': ('이', '가'),
    '은': ('은', '는'), '는': ('은', '는'),
    '과': ('과', '와'), '와': ('과', '와'),
    '아': ('아', '야'), '야': ('아', '야'),
    '이나': ('이나', '나'), '나': ('이나', '나'),
    '이란': ('이란', '란'), '란': ('이란', '란'),
}


def correct_josa(word, josa):
    """
    치환된 단어의 받침에 맞게 조사를 교정합니다.
    (기존에는 파파고 한-일-한 역번역으로 조사를 교정했으나, 해당 API가
    서비스 종료되어 결정론적 규칙 교정으로 대체 — 더 빠르고 항상 동작)
    """
    if josa in ('으로', '로'):
        return '로' if (not has_jongseong(word) or ends_with_rieul(word)) else '으로'
    pair = JOSA_BY_JONGSEONG.get(josa)
    if pair:
        return pair[0] if has_jongseong(word) else pair[1]
    return josa


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
        동음이의어 후보 단어는 딥러닝 모델을 사용하여 의미를 검증하고,
        치환된 단어 바로 뒤의 조사는 받침 규칙에 맞게 교정합니다.
        """
        std_news = copy.deepcopy(mor_sentences)
        mean_news = copy.deepcopy(mor_sentences)
        replaced_sentence_rows = set()
        replaced_terms = []

        for word in use_jargon_list:
            # use_jargon_dict[word] 구조: [std_name, mean_s, [row1, col1], [row2, col2], ...]
            # 따라서 index 2 이후부터 실제 매칭된 단어의 위치 정보
            for loc_info in use_jargon_dict[word][2:]:
                row, column = loc_info[0], loc_info[1]

                # 동음이의어 검증이 필요한 단어인 경우
                if word in homonym_dict:
                    spacing_sentence = self.restore_spacing(mor_sentences[row])
                    if not (self.model_manager and self.model_manager.check_homonym(word, spacing_sentence)):
                        continue  # 전문용어 용법이 아니면 치환하지 않음

                self._apply_replacement(std_news, row, column, use_jargon_dict[word][0])
                self._apply_replacement(mean_news, row, column, use_jargon_dict[word][1])
                replaced_sentence_rows.add(row)
                replaced_terms.append({
                    'jargon': word,
                    'std': use_jargon_dict[word][0],
                    'mean': use_jargon_dict[word][1],
                    'homonym_checked': word in homonym_dict,
                })

        return std_news, mean_news, list(replaced_sentence_rows), replaced_terms

    def _apply_replacement(self, news_structure, row, column, new_word):
        # Okt.pos 튜플 구조 (word, pos) 에서 word 값만 새로운 단어로 교체
        pos_tag_list = list(news_structure[row][column])
        pos_tag_list[0] = new_word
        news_structure[row][column] = tuple(pos_tag_list)

        # 치환된 단어 바로 뒤가 조사라면 받침 규칙에 맞게 교정
        next_col = column + 1
        if next_col < len(news_structure[row]):
            next_word, next_pos = news_structure[row][next_col]
            if next_pos == 'Josa':
                # 설명문 치환처럼 여러 어절로 끝나는 경우 마지막 어절 기준
                last_word = new_word.split()[-1] if new_word.split() else new_word
                news_structure[row][next_col] = (correct_josa(last_word, next_word), next_pos)

    def select_best_sentences(self, std_news, mean_news, replaced_rows):
        """
        표준어 치환 문장과 설명문 치환 문장의 의미 유사도를 KoBERT로 비교하여,
        의미가 크게 달라진 경우(유사도 0.9 이하) 더 설명적인 문장을 선택합니다.
        """
        std_sentence_news = [self.restore_spacing(s) for s in std_news]
        mean_sentence_news = [self.restore_spacing(m) for m in mean_news]

        final_sentences = copy.deepcopy(std_sentence_news)

        for idx in replaced_rows:
            if self.model_manager:
                sim_score = self.model_manager.calculate_similarity(
                    [std_sentence_news[idx]], [mean_sentence_news[idx]]
                )[0]
                # 유사도가 낮으면(0.9 이하) 의미가 훼손되었을 우려가 있으므로 더 설명적인 의미문(mean) 선택
                if sim_score <= 0.90:
                    final_sentences[idx] = mean_sentence_news[idx]
                else:
                    final_sentences[idx] = std_sentence_news[idx]
            else:
                final_sentences[idx] = std_sentence_news[idx]

        return ". ".join(final_sentences)
