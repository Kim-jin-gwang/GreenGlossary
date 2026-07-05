import os
import zipfile
import sys

try:
    import gdown
except ImportError:
    print("[Error] 'gdown' 라이브러리가 설치되어 있지 않습니다.")
    print("다음 명령어를 터미널에 실행하여 설치해 주세요:")
    print("pip install gdown")
    sys.exit(1)

def download_and_extract():
    # 1. model 폴더가 없으면 생성
    model_dir = os.path.join(os.path.dirname(__file__), "model")
    os.makedirs(model_dir, exist_ok=True)
    
    # 2. 구글 드라이브 파일 ID (모델 압축 파일 업로드 후 여기에 ID를 넣어주세요)
    # 예: https://drive.google.com/file/d/1A2B3C4D5E... 에서 "1A2B3C4D5E..." 부분
    file_id = "1f4cVmJtvJFn-Vlad9osga4UAmhtBhZPW" 
    
    if file_id == "구글_드라이브_파일_ID를_여기에_입력하세요":
        print("[Warning] download_models.py 내에 구글 드라이브 파일 ID를 설정해야 합니다.")
        print("구글 드라이브에 모델 폴더들을 하나로 압축하여 업로드한 후, 공유 링크의 파일 ID를 입력해 주세요.")
        sys.exit(1)
        
    url = f"https://drive.google.com/uc?id={file_id}"
    zip_path = os.path.join(model_dir, "models.zip")
    
    # 3. 모델 다운로드
    print("[INFO] Google Drive로부터 모델 압축파일을 다운로드합니다...")
    try:
        gdown.download(url, zip_path, quiet=False, use_cookies=False)
    except Exception as e:
        print(f"[Error] 다운로드 실패: {e}")
        print("공유 링크 권한이 '링크가 있는 모든 사용자'로 설정되어 있는지 확인해 주세요.")
        sys.exit(1)
        
    # 4. 압축 해제
    print("[INFO] 압축을 해제하고 있습니다...")
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # zip 파일 내부에 모델 폴더들(KoBERT_similarity 등)이 바로 들어가 있어야 합니다.
            zip_ref.extractall(model_dir)
        print("[INFO] 압축 해제 완료.")
    except Exception as e:
        print(f"[Error] 압축 해제 실패: {e}")
        sys.exit(1)
    finally:
        # 다운로드받은 임시 zip 파일 삭제
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
    print("[INFO] 모델 파일 세팅이 완료되었습니다!")

if __name__ == "__main__":
    download_and_extract()
