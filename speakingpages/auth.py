from flask import  Blueprint, jsonify, request
from speakingpages import mysql, bcrypt

auth = Blueprint('auth', __name__)


@auth.route('/sign_up' , methods=['POST'])
def sign_up():
    cur = mysql.connection.cursor()
    cur.execute("SELECT email, first_name FROM user")
    users_data = cur.fetchall()
    users_emails = [data[0] for data in users_data] 
    users_names = [data[1] for data in users_data]
    data = request.get_json()
    print(f"Sign Up: {data}")
    name = data['name']
    email = data['email']
    password = data['password']
    if email in users_emails:
        cur.close()
        return jsonify({"message":"هذا الايميل موجود بالفعل" , "status":0})
    elif name in users_names:
        cur.close()
        return jsonify({"message":"هذا الاسم موجود بالفعل ، ادخل اسم آخر", "status":0})
    else:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur.execute("insert into user (first_name, email, password) values (%s, %s, %s)", (name, email,hashed_password ))
        mysql.connection.commit()
        # helpful link: https://g.co/gemini/share/45256f2afd48
        cur.execute("SELECT id FROM user WHERE email = %s", (email,))
        user_id = cur.fetchone()[0]
        cur.close()  

        return jsonify({"message":"تم انشاء حساب بنجاح", "status":1, 
                        "user_id": user_id , "user_name": name, "email": email})
    
        
@auth.route('/login' , methods=['POST'])
def login():
    cur = mysql.connection.cursor()
    cur.execute("SELECT email, password FROM user")
    users = cur.fetchall()
    users_data = {data[0]: data[1] for data in users}   #users_data = {"email":"passowrd"}

    data = request.get_json()
    print(f"Login: {data}")
    email = data['email']
    password = data['password']
    if email not in users_data:
        cur.close()
        return jsonify({"message":"هذا الايميل غير موجود", "status":0}) 
    else:
        if bcrypt.check_password_hash(users_data[email], password):
            cur.execute("SELECT id FROM user WHERE email = %s", (email,))
            user_id = cur.fetchone()[0]
            cur.execute("SELECT first_name FROM user WHERE email = %s", (email,))
            user_name = cur.fetchone()[0]
            cur.close()
            return jsonify({"message": "تم إدخال البيانات بنجاح", "status":1, 
                            "user_id": user_id, "user_name": user_name , "email": email})
        else:
            cur.close()
            return jsonify({"message":"كلمة السر غير صحيحة", "status":0})
   
