from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'notice': 'I am a test msg'})


if __name__ == '__main__':
    app.run(debug=True)