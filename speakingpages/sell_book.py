from decimal import Decimal
from flask import  Blueprint, jsonify, request
from speakingpages import mysql

used_book = Blueprint('used_book', __name__)

    
@used_book.route('/sell_book', methods=['POST'])
def sell_book():
    cur = mysql.connection.cursor()
    data = request.get_json()
    if request.method == 'POST':
        book_id = data['book_id']
        book_status = data['book_status']
        book_price = Decimal(data['book_price'])
        phone = data['phone']
        name = data['name']
        address = data['address']
        cur.execute("""insert into `used available books`
                    (price, book_status , book_id , seller_name , seller_phone , seller_address)
                    values (%s, %s, %s, %s, %s, %s)""", 
                    (book_price, book_status, book_id, name, phone, address))
        mysql.connection.commit()
        return jsonify({"message": "تم اضافة الكتاب بنجاح"})
    cur.close()

@used_book.route('/show_used_books/<int:book_id>')
def show_used_books(book_id):
    cur = mysql.connection.cursor()
    cur.execute("select book_id from `used available books` where book_id = %s", (book_id,))
    is_book_exist = cur.fetchone()
    if is_book_exist == None:
        print("no used books for this book")
        return {}, 200
    else:
        cur.execute("""select book.book_name , seller_name , seller_address , seller_phone, price , book_status
                        from `used available books`
                        INNER JOIN book ON  `used available books`.book_id = book.id
                        where book_id = %s""", (book_id,))
        books_data = cur.fetchall()
        used_book = []
        for data in books_data:
            used_book.append({'book_name': data[0],'seller_name': data[1], 'address': data[2], 'phone': data[3], 'price': data[4], 'book_status': data[5]})
        cur.close() 
        return used_book
     
    