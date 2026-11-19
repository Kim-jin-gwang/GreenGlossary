# 🌱 농림 전문용어 순화 번역기 (GreenGlossary)

> **어려운 산림·농업 한자어를 쉬운 우리말 문장으로 바꿉니다.**
> **Project Date:** 2022.09 ~ 2022.12 · **3인 팀 프로젝트** (상명대학교 캡스톤 디자인) · 2026.08 라이브 데모 리팩터링
> **Platform:** 웹 (Flask 로컬 앱 · Gradio API + 커스텀 프론트엔드 라이브 데모)
> **Role:** 아이디어 구상·문제 정의 · 용어 사전 구축·키워드 추출 · 역번역 시스템 구축 · NLP 모델링
> **Live Demo:** [demo-gateway.trealight112.workers.dev/greenglossary](https://demo-gateway.trealight112.workers.dev/greenglossary/)

산림·농업 분야 문서에는 "간벌", "복토", "몽리 면적" 같은 한자어 전문용어가 많아 일반인이 읽기 어렵습니다. GreenGlossary는 **직접 구축한 전문용어 사전**과 **KoBERT 모델 4종**을 결합해, 이런 문장을 **쉬운 우리말로 자동 순화**합니다.

사전은 용어를 찾아 바꾸는 **치환 도구**이고, 품질을 결정하는 것은 **바꿔도 되는지(동음이의어 판별)** 와 **바꾼 뒤에도 뜻이 남는지(문장 유사도 검사)** 를 확인하는 검증 단계입니다.

---

## 📱 실제 화면

| 전문용어 순화 | 동음이의어 판별 |
|:---:|:---:|
| <img src="docs/images/screenshots/01-result.png" width="420" alt="전문용어 순화 결과"/> | <img src="docs/images/screenshots/02-homonym.png" width="420" alt="동음이의어 판별 결과"/> |
| 문장 속 전문용어를 쉬운 말로 바꾸고 바뀐 용어를 함께 표시 | 문맥상 전문용어가 아닌 낱말은 바꾸지 않고 그대로 둠 |

---

## 📖 프로젝트 개요

전문용어를 쉬운 말로 1:1 치환하는 것만으로는 읽을 수 있는 문장이 나오지 않습니다. 같은 글자가 일상어로 쓰인 경우까지 바꿔 버리고, 바꾼 단어의 받침이 달라져 조사가 어색해지며, 짧은 순화어로는 원래 뜻이 빠지기도 합니다.
GreenGlossary는 이 세 가지를 **사전 매칭 + 문맥 판별 + 조사 교정 + 의미 검증**으로 나누어 풉니다.

* **한국어 전문용어 데이터셋이 없어 사전을 직접 구축** — 국립국어원 표준 전문용어 사전을 크롤링해 전문용어·순화어·설명문을 한 행으로 묶음
* **글자 일치가 아닌 문맥 판별** — "도장"(찍는 도장 / 나무의 도장지)처럼 일상어와 겹치는 용어는 전문용어 용법일 때만 치환
* **순화어와 설명문 두 가지 버전** — 짧은 순화어로 바꾼 문장의 뜻이 달라지면 더 설명적인 문장을 선택

### 💡 주요 기능

| 기능 | 설명 |
|---|---|
| 🔍 **전문용어 사전 매칭** | Okt 형태소 분석 후 용어 사전과 대조해, 문장 번호·토큰 위치 단위로 치환 대상을 기록 |
| 🧠 **동음이의어 문맥 판별** | 도장·도복·화형 3개 용어는 용어별 KoBERT 분류 모델이 문장 문맥을 보고 전문용어 용법일 때만 치환 |
| ✏️ **조사 자동 교정** | 치환 후 받침이 달라지면 뒤따르는 조사(을/를, 이/가, 은/는, 과/와, 으로/로 등)를 맞춤 (예: "간벌**을**" → "솎아베기**를**") |
| ⚖️ **의미 보존 문장 선택** | 순화어 버전과 설명문 버전을 KoBERT 문장 유사도로 비교해, 유사도 0.9 이하이면 설명문 버전 채택 |
| 🏷️ **치환 내역 반환** | 라이브 데모 API는 용어·순화어·설명·동음이의어 판별 여부를 구조화해 반환하고, 프론트엔드가 하이라이트와 카드로 표시 |

---

## 🏗️ 아키텍처 — 사전 치환 + KoBERT 검증

모든 용어를 모델로 번역하지 않고, **사전이 치환을 맡고 KoBERT는 치환의 앞뒤를 검증**하는 구조로 나눴습니다.

```mermaid
flowchart LR
    A[입력 문장] --> B[Okt 형태소 분석<br>+ 용어 사전 매칭]
    B --> C{동음이의어?<br>도장·도복·화형}
    C -->|예| D[KoBERT 문맥 판별<br>전문용어 용법인지 검증]
    C -->|아니오| E[치환]
    D -->|전문용어 맞음| E
    D -->|일반 단어| F[치환 안 함]
    E --> G[받침 규칙 기반<br>조사 자동 교정]
    G --> H[KoBERT 유사도 비교<br>순화어 vs 설명문 선택]
    H --> I[쉬운 우리말 문장]
```

**요청 흐름 (문장 입력 → 순화 문장)**

1. 입력 텍스트를 문장 단위로 나누고 Okt로 형태소 분석한 뒤, 토큰을 용어 사전과 대조해 위치를 기록
2. 동음이의어 후보(도장·도복·화형)는 해당 용어의 KoBERT 분류 모델에 문장을 넣어, 예측값 0.8 이상일 때만 치환 대상으로 확정
3. 같은 문장을 **순화어 버전**과 **설명문 버전** 두 가지로 치환하고, 치환한 단어 바로 뒤의 조사를 받침 규칙으로 교정
4. 두 버전의 KoBERT 문장 유사도가 0.9 이하이면 설명문 버전을, 아니면 순화어 버전을 선택
5. 문장을 다시 이어 붙여 결과를 반환 (라이브 데모 API는 치환 내역도 함께 반환)

> 동음이의어 판별 모델은 용어마다 따로 학습해야 하므로, 사전 전체가 아니라 일상어와 실제로 겹치는 3개 용어에만 모델을 붙이고 나머지는 사전 치환으로 처리했습니다.

### 🌐 라이브 데모 아키텍처

```text
[커스텀 프론트엔드]                        [백엔드 API]                       [모델 저장소]
Cloudflare                          ──▶ HF Space: kimjgwang/ml-demos  ──▶ HF Model: greenglossary-kobert
demo-gateway/greenglossary/             /simplify API (Py 3.11·TF 2.15)    KoBERT SavedModel 4종 (1.3GB)
문장 입력·용어 하이라이트/카드            Cafe-Focusing과 통합 호스팅          기동 시 snapshot_download
```

* HF 무료 티어 제약(ZeroGPU Space 2개, Space 저장소 1GB)에 맞춰 **백엔드는 통합 Space**([kimjgwang/ml-demos](https://huggingface.co/spaces/kimjgwang/ml-demos))에서, **모델은 별도 Model 저장소**([kimjgwang/greenglossary-kobert](https://huggingface.co/kimjgwang/greenglossary-kobert))에서 제공
* KoNLPy(Okt)의 JVM 의존성은 HF `packages.txt`(default-jre)로 해결
* 추론은 CPU에서 실행해 방문자별 ZeroGPU 쿼터를 쓰지 않음

### ♻️ 2026 리뉴얼 (라이브 데모 개편)

| 분류 | 원래 구현 (2022 캡스톤) | 리팩터링 후 (2026.08) |
|---|---|---|
| **조사 교정** | Papago API 한-일-한 역번역 | API 서비스 종료로 동작 불가 → 형태소 태그 기반 **결정론적 조사 교정 규칙**으로 대체 (외부 API 의존 제거, 항상 동작, 즉시 응답) |
| **서버 구조** | Flask 단일 앱 | **Gradio API 서버(`demo_api.py`) + 커스텀 프론트엔드** 2-티어 구조. Flask 앱(`app.py` + `server.py`)은 로컬 실행용으로 유지 |
| **응답 형식** | 순화된 문장만 화면에 표시 | 치환 내역(용어/순화어/설명/동음이의어 판별 여부)을 구조화해 반환 — 프론트에서 하이라이트 표시 |
| **모델 배포** | gdown(구글 드라이브) 다운로드 | 링크 만료·쿼터 문제로 **Hugging Face Hub**(`download_models.py`)로 교체 |
| **정리** | — | 미사용 파일 제거(구 번역기, 템플릿 README, 무관한 이미지), eager import 정리, 하드코딩됐던 API 키는 이전에 폐기·제거 완료 |

---

## 🔬 순화 파이프라인 4단계

각 단계는 `src/nlp_processor.py`의 함수 하나에 대응하고, 모델이 없어도 1·3단계(사전 매칭·조사 교정)는 그대로 동작합니다.

| 단계 | 역할 | 방법 |
|---|---|---|
| **1. 사전 매칭** | 문장에서 전문용어와 위치 찾기 | Okt 형태소 분석 결과를 용어 사전(전문용어 → 순화어·설명문)과 대조. 매칭 결과는 요청마다 새로 만들어 요청 간 상태가 섞이지 않게 함 |
| **2. 동음이의어 판별** | 일상어로 쓰인 경우 치환 제외 | 도장·도복·화형 용어별 KoBERT 이진 분류 모델. 예측값 0.8 이상이면 전문용어 용법으로 판정 |
| **3. 치환 + 조사 교정** | 순화어·설명문 두 버전 생성 | 토큰을 교체한 뒤, 바로 뒤 토큰이 조사면 마지막 어절의 받침(으로/로는 ㄹ 받침까지)에 맞춰 교정 |
| **4. 문장 선택** | 뜻이 훼손된 치환 걸러내기 | 두 버전의 KoBERT 문장 임베딩 유사도를 계산해 0.9 이하이면 설명문 버전, 초과이면 순화어 버전 채택 |

---

## 📊 데이터 규모와 실측

| 단계 | 결과 |
|---|---|
| **용어 사전 구축** | 국립국어원 표준 전문용어 사전 크롤링으로 전문용어-대체어 매핑 **951개** 구축 |
| **저장소 포함 사전** | `data/agriculture_dictionary.xlsx` — 810행, 고유 전문용어 **801개** (전문용어 · 순화어 · 설명문 3열) |
| **동음이의어 판별** | KoBERT 파인튜닝으로 판별 정확도 **99.0%** (기존 약 30.8 → 99.0) |
| **실문서 변환 테스트** | 농업 뉴스 100건 중 **93건** 자연스러운 변환 |
| **모델** | KoBERT SavedModel **4종 · 약 1.3GB** (문장 유사도 1종 + 동음이의어 판별 3종) |

---

## 🛠️ 기술 스택

| 영역 | 스택 |
|---|---|
| **NLP** | <img src="https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/TensorFlow_2.15-FF6F00?style=flat-square&logo=tensorflow&logoColor=white"/> KoBERT (문장 유사도 · 이진 분류, tensorflow-text) + KoNLPy Okt (형태소 분석) |
| **백엔드** | <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white"/> <img src="https://img.shields.io/badge/Gradio-F97316?style=flat-square&logo=gradio&logoColor=white"/> |
| **데이터** | <img src="https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white"/> openpyxl (엑셀 기반 용어 사전) · BeautifulSoup (사전 크롤링) |
| **인프라** | <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white"/> <img src="https://img.shields.io/badge/Hugging_Face_Spaces·Hub-FFD21E?style=flat-square&logo=huggingface&logoColor=black"/> <img src="https://img.shields.io/badge/Cloudflare-F38020?style=flat-square&logo=cloudflare&logoColor=white"/> |
| **원래 구현 (2022)** | Papago API 한-일-한 역번역 (서비스 종료로 2026 리뉴얼에서 규칙 기반 교정으로 대체) |

---

## 💥 트러블 슈팅

### 1. 쓸 수 있는 한국어 전문용어 데이터셋이 없었다
* **현상:** 농·임업 전문용어와 쉬운 대체어를 짝지은 공개 데이터셋이 없어 치환할 기준 자체가 없었음.
* **해결:** 국립국어원 표준 전문용어 사전을 크롤링해 전문용어-대체어 매핑 사전 951개를 직접 구축. 팀원이 같은 형식으로 채울 수 있도록 데이터 템플릿을 만들어 작업을 나눔.

### 2. 같은 글자가 일상어로도 쓰였다
* **현상:** "도복", "도장"처럼 문맥에 따라 뜻이 달라지는 단어를 사전 일치만으로 치환하면 전문용어가 아닌 문장까지 바뀜.
* **원인:** 사전 매칭은 글자만 보고 문장의 뜻을 보지 않음.
* **해결:** 용어별로 KoBERT를 파인튜닝해 문장 문맥으로 전문용어 용법 여부를 판별. 판별 정확도 99.0% (기존 약 30.8 → 99.0).

### 3. 1:1로 바꾸면 조사가 어색해졌다
* **현상:** 치환한 단어의 받침이 원래 단어와 달라 "솎아베기을"처럼 조사가 맞지 않는 문장이 나옴.
* **해결 (원래 구현):** Papago API 한-일-한 역번역으로 조사를 자연스럽게 교정. 일본어에 미래 시제가 없어 시제가 사라지는 문제는 "현재형 동사 + 시간 부사" 조합 로직으로 보완.
* **해결 (2026 리뉴얼):** 해당 API가 서비스 종료되어 역번역이 동작하지 않게 되자, Okt 형태소 태그로 조사를 찾아 받침 유무에 따라 고르는 결정론적 규칙으로 대체. 외부 API 없이 항상 동작하고 즉시 응답.

### 4. 짧은 순화어로는 뜻이 빠졌다
* **현상:** 순화어 한 단어로 바꾸면 원래 용어가 담던 뜻이 일부 사라지는 문장이 있었음.
* **해결:** 순화어 버전과 설명문 버전을 모두 만들고 KoBERT 문장 유사도를 계산해, 0.9 이하이면 설명문 버전을 채택. 판별 · 조사 교정 · 유사도 검사를 잇는 변환 절차로 정리.

### 5. Windows에서는 모델 추론을 할 수 없었다
* **현상:** 로컬(Windows)에서 KoBERT 모델을 불러올 수 없어 추론 결과를 확인할 수 없었음.
* **원인:** KoBERT 구동에 필요한 `tensorflow-text`가 Windows 휠을 제공하지 않음. 모델은 TF2 SavedModel(Keras 2) 형식이라 버전도 2.15로 고정해야 함.
* **해결:** Python 3.11 + TensorFlow 2.15 + JRE를 담은 Linux 도커 이미지를 만들어 어디서든 같은 환경으로 실행·검증.

### 6. 요청이 쌓일수록 이전 요청의 매칭 위치가 섞였다
* **현상:** 서버로 띄우면 앞선 요청에서 기록한 용어 위치가 다음 요청 결과에 누적됨.
* **원인:** 매칭 위치를 공유 사전 객체에 직접 덧붙이고 있었음.
* **해결:** 공유 사전은 읽기만 하고, 매칭 결과는 요청마다 새 객체로 만들도록 변경.

---

## 📂 디렉터리 구조

```text
GreenGlossary/
├── demo_api.py             # 라이브 데모용 Gradio API 서버 (HF Spaces 진입점)
├── app.py / server.py      # Flask 웹앱 (로컬 실행용)
├── config.py               # 모델 · 데이터 경로 설정
├── download_models.py      # KoBERT 모델 다운로드 스크립트 (HF Hub)
├── Dockerfile              # 도커 이미지 (py3.11 + TF 2.15 + JRE, 모델 자동 다운로드)
├── requirements.txt        # 의존성 (TF 2.15 고정 — SavedModel 호환)
├── packages.txt            # HF Spaces 시스템 패키지 (JVM)
├── data/
│   └── agriculture_dictionary.xlsx  # 전문용어 사전 (전문용어 · 순화어 · 설명문)
├── src/
│   ├── dictionary.py       # 용어 사전 로더
│   ├── models.py           # KoBERT 모델 매니저 (유사도 · 동음이의어)
│   └── nlp_processor.py    # 매칭 · 치환 · 조사 교정 · 문장 선택 파이프라인
├── templates/              # Flask 화면 (home.html · after.html · css/)
└── model/                  # KoBERT 모델 4종 (git 미추적 — download_models.py로 다운로드)
```

---

## 🚀 실행 방법

**요구 사항:** Docker (권장) 또는 Linux + Python 3.11 + JRE (KoNLPy Okt용)

```bash
docker build -t greenglossary .
docker run -p 5000:5000 greenglossary   # Flask 웹앱 http://localhost:5000
```

KoBERT 모델(약 1.3GB)은 컨테이너 기동 시 HF 모델 저장소에서 자동으로 내려받습니다.

Linux에서 직접 실행할 때:

```bash
pip install -r requirements.txt   # tensorflow-text는 Windows 미지원
python download_models.py         # KoBERT 모델 다운로드 (약 1.3GB, HF Hub)
python demo_api.py                # Gradio API/UI http://localhost:7860
python server.py                  # 또는 Flask 웹앱 http://localhost:5000
```

Windows에서 직접 실행하면 `tensorflow-text` 휠이 없어 모델 추론이 불가하므로 도커 방식을 사용합니다. 사전 매칭·조사 교정 로직은 모델 없이도 동작합니다 (`konlpy`, `pandas`, `openpyxl`만 설치).

---

## 데이터 출처

- 국립국어원 표준 전문용어 사전 — 전문용어·순화어·설명문 수집 원천
