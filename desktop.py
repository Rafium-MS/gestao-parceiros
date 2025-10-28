
import sys, threading, time, webbrowser
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView

def run_flask():
    # Run the Flask app in this thread
    from app import create_app
    app = create_app()
    # Use waitress to avoid reloader threads
    from waitress import serve
    serve(app, host="127.0.0.1", port=5000)

if __name__ == "__main__":
    # Start Flask server
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    # Wait a moment for server
    time.sleep(1.2)

    # PyQt WebView
    app_qt = QApplication(sys.argv)
    view = QWebEngineView()
    view.setWindowTitle("Disagua Desktop")
    view.resize(1280, 800)
    view.load(QUrl("http://127.0.0.1:5000/"))
    view.show()
    sys.exit(app_qt.exec_())
