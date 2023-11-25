from flask import Flask, render_template, jsonify
import speedtest
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/login/')
def login():
    return render_template('login page.html')

@app.route('/signup/')
def signup():
    return render_template('signup.html')
``
@app.route('/run-speedtest')
def run_speedtest():
    st = speedtest.Speedtest()
    download_speed = st.download()
    upload_speed = st.upload()

    # Convert speeds to Mbps
    download_speed_mbps = download_speed / 10**6
    upload_speed_mbps = upload_speed / 10**6

    return jsonify({
        'downloadSpeed': download_speed_mbps,
        'uploadSpeed': upload_speed_mbps
    })

if __name__ == '__main__':
    app.run(debug=True)
