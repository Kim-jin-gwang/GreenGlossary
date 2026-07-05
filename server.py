from app import app, get_model_manager

if __name__ == "__main__":
    print("[INFO] Pre-initializing models on startup...")
    get_model_manager()
    app.run(debug=True, host="127.0.0.1", port=5000)

