import json
from flask import  Blueprint, Response, jsonify, render_template, request
from speakingpages import mysql


field = Blueprint("field", __name__)

#unused function
# @field.route("/field" , methods=['GET', 'POST'])
# def choose_field():
#     cur = mysql.connection.cursor()
#     if request.method == 'GET':
#         cur.execute("SELECT field_name FROM field")
#         fields_data = cur.fetchall()
#         field_names = [data[0] for data in fields_data]
#         return field_names
#     if request.method == 'POST':
#         #should handle if the user enter not existing field_id
#         field_id = request.form['field_id']
#         cur.execute("SELECT field_name FROM field where id = %s", (field_id, ))
#         field_name = cur.fetchone()[0]
#         return field_name
        
#     cur.close()

#'1', 'ديني'
# '2', 'ثقافي'
# '3', 'أدبي'


# function to get books in each field
@field.route("/cultural_books", methods=['GET'])
def cultural_books():
    cur = mysql.connection.cursor()
    cur.execute("select id, book_name, image_url from book where book_field = 2")
    cultural_data = cur.fetchall()
    cultural_books = []
    for data in cultural_data:
        book = {"book_id": data[0], "book_name": data[1], "book_image": data[2]}
        cultural_books.append(book)
    cur.close()
    return jsonify(cultural_books)

@field.route("/literature_books", methods=['GET'])
def literature_books():
    cur = mysql.connection.cursor()
    cur.execute("select id , book_name, image_url  from book where book_field = 3")
    literature_data = cur.fetchall()
    literature_books = []
    for data in literature_data:
        book = {"book_id": data[0], "book_name": data[1], "book_image": data[2]}
        literature_books.append(book)
    cur.close()
    return jsonify(literature_books)

@field.route("/relgious_books", methods=['GET'])
def relgious_books():   
    cur = mysql.connection.cursor()
    cur.execute("select id, book_name, image_url from book where book_field = 1")
    result = cur.fetchall()
    books_dict = []
    for data in result:
        book_dict = {
            "book_id": data[0],
            "book_name": data[1],
            "book_image": data[2]
        }
        books_dict.append(book_dict)
    cur.close()
    return jsonify(books_dict)
    # response = Response(json.dumps(books_dict, ensure_ascii=False),
    #                      content_type="application/json; charset=utf-8" )
    # return response
