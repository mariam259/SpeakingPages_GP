from flask import  Blueprint, render_template, request
from decimal import Decimal

from speakingpages import mysql
# from .event import get_messages


book = Blueprint('book', __name__)

#function to show details of a book (book description page)
@book.route('/book_details/<int:book_id>')
def show_book(book_id):
    cur = mysql.connection.cursor()
    query = """select book_name , book_discription , book_price , 
                author, image_url , field.field_name, library.library_name
                from book
                INNER JOIN field ON book.book_field = field.id  
                INNER JOIN library ON book.library_id = library.id  
                where book.id = %s"""
    cur.execute(query, (book_id, ))
    book_data = cur.fetchall()
    cur.close()
    for data in book_data:
        book_dic = {'book_name': data[0],'discription': data[1], 'book_price': data[2], 
                    'author': data[3], 'image_url': data[4], 'field_name': data[5], 'library_name': data[6]}
    cur.close()
    return book_dic    
