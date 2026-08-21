import os

from app import app, get_model_manager

if __name__ == "__main__":
    print("[INFO] Pre-initializing models on startup...")
    get_model_manager()
    # 도커 등 외부 노출이 필요한 환경에서는 HOST=0.0.0.0 으로 실행
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )
