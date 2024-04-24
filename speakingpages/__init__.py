from flask import Flask
from flask_mysqldb import MySQL
# from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import  SocketIO
# from flask_ngrok import run_with_ngrok

app = Flask(__name__)
# Replace with your actual ngrok auth token
# auth_token = "2cQHq1jBFtoSgY50OjDHjnboX5d_73G211A6CvjP5F1KiXKRt"

# Configure ngrok using the auth token

# adding mysql config for my database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mariam2024'
app.config['MYSQL_DB'] = 'speakingpages'


# app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51OnsGPFcaomoWuq20p8mcEPHx2uYUIr0Ay8oGbD1K2juNxZnxbL2NbWMM3EWzfAmhcLjy9AE29iNaiu6irP21FiE00QnPokeIv'
# app.config['STRIPE_SECRET_KEY'] = 'sk_test_51OnsGPFcaomoWuq2X3mUJC7vp0t5F6kwsM5T3WcsoHnm9qVLrpkIBKPSFH4EP6DmMs2M69ztKbr07Q2ATANc74Pi00QwJQrhYA'
# create an object from mysql class
mysql = MySQL(app)
# login_manager = LoginManager()
bcrypt = Bcrypt(app)
socketio = SocketIO(app)

from speakingpages.auth import auth
app.register_blueprint(auth, url_prefix='/')
# login_manager.login_view = 'auth.login'
# login_manager.init_app(app)

# from speakingpages.chat_room import book_chat
# app.register_blueprint(book_chat, url_prefix='/')

from speakingpages.sell_book import used_book
app.register_blueprint(used_book, url_prefix='/')

from speakingpages.field import field
app.register_blueprint(field, url_prefix='/')

from speakingpages.books import book
app.register_blueprint(book, url_prefix="/")

from speakingpages.book_club import book_club
app.register_blueprint(book_club , url_prefix="/")
# from speakingpages.event import book_discussion
# app.register_blueprint(book_discussion, url_prefix="/")

from speakingpages.cart import cart
app.register_blueprint(cart, url_prefix='/')

from speakingpages.payment import payment
app.register_blueprint(payment, url_prefix='/')

from speakingpages.reading_plan import reading_plan
app.register_blueprint(reading_plan, url_prefix='/')

