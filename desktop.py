
import sys, threading, time
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView

def run_flask():
    from app import create_app
    from waitress import serve
    app = create_app()
    serve(app, host="127.0.0.1", port=5000)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    time.sleep(1.0)

    app_qt = QApplication(sys.argv)
    view = QWebEngineView()
    view.setWindowTitle("Disagua Desktop")
    view.resize(1280, 800)
    view.load(QUrl("http://127.0.0.1:5000/login"))
    view.show()
    sys.exit(app_qt.exec_())
