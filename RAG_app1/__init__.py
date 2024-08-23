from flask import Flask

app = Flask(__name__)

import RAG_app1.main  # main.pyをインポートしてルートを登録