import json
from flask import session
from speakingpages import socketio,mysql


def check_if_user_is_admin(name):
    cur = mysql.connection.cursor()
    cur.execute("select user_id from `book club admin` where name = %s", (name,))
    admin_id = cur.fetchone()[0]
    if admin_id is None:
        return False
    cur.close()
    return True

#return all the messages with usernames in specific book disscussion
def get_messages(book_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT  `book dis`.message, user.first_name ,`book dis`.id
                    from `book dis`
                    INNER JOIN user ON `book dis`.user_id = user.id
                    where `book dis`.book_id = %s """ , (book_id,))
    result = cursor.fetchall()
    messages = []
    for data in result:
        message = {"username": data[1], "text": data[0] , "id": data[2]}
        messages.append(message)
    cursor.close()
    return messages

def save_message(user_name, message, book_id):
    cur = mysql.connection.cursor()
    #need to handle if two users have the same name
    cur.execute("SELECT id FROM user WHERE first_name = %s", (user_name,))
    user_id = cur.fetchone()[0]
    cur.execute("INSERT INTO `book dis` (book_id, user_id, message) VALUES (%s, %s, %s)",
                (book_id, user_id, message))
    mysql.connection.commit()
    cur.execute("""select id from `book dis` where message = %s
                   ORDER BY `book dis`.message_time DESC
                   limit 1 """ , (message,))
    message_id = cur.fetchone()[0]
    cur.close()
    return message_id


def get_club_messages(club_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT  `club discussion`.message, user.first_name , `club discussion`.id
                    from `club discussion`
                    INNER JOIN user ON `club discussion`.user_id = user.id
                    where `club discussion`.club_id =  %s """ , 
                    (club_id,))
    result = cursor.fetchall()
    club_messages = []
    for data in result:
        if(check_if_user_is_admin(data[1])):
            message = {"username": "مشرف النادي", "text": data[0], "id": data[2]}
        else:
            message = {"username": data[1], "text": data[0], "id": data[2]}
        club_messages.append(message)
    cursor.close()
    return club_messages


def save_club_message(club_id,user_name, message):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM user WHERE first_name = %s", (user_name,))
    user_id = cur.fetchone()[0]
    cur.execute("INSERT INTO `club discussion` (club_id, user_id, message) VALUES (%s, %s, %s)",
                (club_id, user_id, message))
    mysql.connection.commit()
    cur.execute("""select id from `club discussion` where message = %s
                    ORDER BY `club discussion`.message_time DESC
                    limit 1""" , (message,))
    message_id = cur.fetchone()[0]
    cur.close()
    return message_id




@socketio.on("connect")
def handle_connect():
    print("user connected")

#join need to handle so that it not join the same room multiple times
@socketio.on('join')
def handle_join(data):
    print(f"Android joining book: {data}")
    book_id = data
    session['book_id'] = book_id
    messages_data = get_messages(book_id)
    print("messages_data: ", messages_data)
    socketio.emit("load_messages", messages_data)
    print("loaded messages")
    

@socketio.on('new_message')
def handle_send_message(data):
    print(f"Android: {data}")
    res = json.loads(data)
    user_name = (res["username"])
    content = (res["text"])
    book_id = session.get('book_id')
    msg_id = save_message(user_name, content , book_id)
    message_data = {"username": user_name, "text": content, "id": msg_id}
    print("book msg sent:" , message_data)
    socketio.emit("broadcast", message_data)
    return print(f"Username: {user_name} send message: {content}")
    # Handle the case where "username" is missing
    # return "can't access the passed data."


@socketio.on('join_club')
def handle_join_club(data):
    print(f"Android joining club: {data}")
    club_id = data
    session['club_id'] = club_id
    print("session club: ", session.get('club_id'))
    messages_data = get_club_messages(club_id)
    print("messages_data: ", messages_data)
    socketio.emit("load_club_messages", messages_data)
    print("club loaded messages")


@socketio.on('new_club_message')
def handle_new_club_message(data):
    print(f"Android club: {data}")
    res = json.loads(data)
    user_name = (res["username"])
    content = (res["text"])
    club_id = session.get('club_id')
    msg_id = save_club_message(club_id, user_name, content)
    if(check_if_user_is_admin(user_name)):
       message_data = {"username": "مشرف النادي", "text": content, "id": msg_id}
    else:
        message_data = {"username": user_name, "text": content, "id": msg_id}
    message_data = {"username": user_name, "text": content, "id": msg_id}
    print("club msg sent:" , message_data)
    socketio.emit("broadcast_club", message_data)
    print(f"user: {user_name} sent message: {content} in club: {session.get('club_id')}")


@socketio.on('disconnect')
def handle_disconnect():
    session.clear()
    print('Client disconnected')





