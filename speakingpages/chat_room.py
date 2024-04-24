# from flask import  Blueprint, request
# from speakingpages import mysql
# # from flask_socketio import  join_room, leave_room, send


# book_chat = Blueprint('book_chat', __name__)

# @book_chat.route('/chat_room/<int:book_id>' , methods=['GET', 'POST'])
# def chat_room(book_id):
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT room_code FROM `chat room` INNER JOIN book ON `chat room`.book_id = book.id WHERE book.id = %s ", (book_id,))
#     result = cur.fetchone()
#     if result:
#         room_code = str(result[0])  # Access the first element of the tuple
#     else:
#         room_code = None  # Handle the case where no room_code is found
        
#     # room_code = result[0][0]
#     # print(f"this is room code {room_code}")
#     cur.execute("""
#                 SELECT  message, user.first_name
#                 FROM `book dis`
#                 INNER JOIN user ON `book dis`.user_id = user.id
#                 INNER JOIN book ON `book dis`.book_id = book.id
#                 INNER JOIN `chat room` ON  `book dis`.room_id = `chat room`.id
#                 where room_code = %s
#                 """, (room_code,))
#     discussions = cur.fetchall()
    
#     user_discussions = {data[1]: data[0] for data in discussions} 
#     #cur.close()
#     if request.method == 'POST':
#         message = request.form['message']
#         user_id = int(request.form['user_id'])
#         #should use current user but request it now for testing
#         # message_time = request.form['message_time']
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT id FROM `chat room` WHERE room_code = %s", (room_code,))
#         res = cur.fetchone()
#         if res:
#             room_id = res[0]
#         else:
#             room_id = None
#         cur.execute("""INSERT INTO `book dis` (message, user_id, book_id, room_id) 
#                     VALUES (%s, %s, %s, %s)""", (message, user_id, book_id, room_id))
#         mysql.connection.commit()
#         cur.close()
#         return f"you enter new message: {message}"
#     if request.method == 'GET':
#         return user_discussions
#     # return user_discussions


# #show chats on a book
# @book_chat.route("/book_messages/<int:book_id>", methods=['GET'])
# def message_test(book_id):
#     cur = mysql.connection.cursor()
#     cur.execute("""select user.first_name, message 
#                 from `book dis`
#                 INNER JOIN user ON `book dis`.user_id = user.id
#                 where book_id = %s""", (book_id,))
#     data = cur.fetchall()
#     messages = []
#     for d in data:
#         message_data = {"username": d[0],"message": d[1]}
#         messages.append(message_data)
#     cur.close()
#     return messages