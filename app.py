

from speakingpages import app, socketio
# from flask_ngrok import run_with_ngrok
# my ip = 192.168.1.6
# my host = http://192.168.1.6:5000
# socketio.run(app)
if __name__ == '__main__':
    # run_with_ngrok(app)
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)

    