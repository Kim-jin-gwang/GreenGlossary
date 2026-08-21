"""KoBERT 모델 다운로드 스크립트.

모델(약 1.3GB)은 용량 문제로 GitHub에 없고 Hugging Face 모델 저장소에
호스팅된다. model/ 폴더가 비어있으면 받아온다. (기존 gdown/구글드라이브
방식은 링크 만료·쿼터 문제가 있어 HF Hub로 교체)
"""
import os
import sys

MODEL_REPO = "kimjgwang/greenglossary-kobert"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")


def main():
    if os.path.isdir(os.path.join(MODEL_DIR, "KoBERT_similarity")):
        print("[download_models] model/ 폴더에 모델이 이미 존재합니다 — 생략")
        return

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("[Error] huggingface_hub가 필요합니다: pip install huggingface_hub")
        sys.exit(1)

    print(f"[download_models] {MODEL_REPO} 에서 모델 다운로드 (~1.3GB)...")
    snapshot_download(repo_id=MODEL_REPO, local_dir=MODEL_DIR)
    print("[download_models] 완료")


if __name__ == "__main__":
    main()
