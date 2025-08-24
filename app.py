from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Aplikasi Flask dari Termux berhasil!</h1><p>Langkah selanjutnya adalah upload ke GitHub.</p>'
