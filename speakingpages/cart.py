from flask import  Blueprint, jsonify, request
from speakingpages import mysql

cart = Blueprint("cart",__name__)

#function for add book to cart button in book details page
@cart.route("/add_book_to_cart", methods=['POST'])
def add_book_to_cart():
    data = request.get_json()
    print("add book to cart: ", data)
    user_id = data['user_id']
    book_id = data['book_id']
    cur = mysql.connection.cursor()
    cur.execute("select id from cart where user_id = %s and status= %s", (user_id,'P' ))
    result = cur.fetchone()     #check if user has a cart
    if (result) is None:    #if user doesn't has a cart create one and add book to it
        cur.execute("INSERT INTO cart (user_id) VALUES (%s)", (user_id,))
        mysql.connection.commit()
        cur.execute("select id from cart where user_id = %s and status= %s", (user_id,'P' ))
        user_cart_id = cur.fetchone()[0]
        print (f"this is the user cart id: {user_cart_id}")
        # return "done"
        cur.execute("select copies_no from `library_available_book` where book_id =%s", (book_id,))
        copy_no = cur.fetchone()[0]
        if copy_no == 0:
            cur.close()
            return jsonify({"message": "لا يوجد نسخ متاحة حاليًا"})
        else:
            cur.execute("""select book_id from `cart item` where cart_id = %s and book_id = %s""", (user_cart_id, book_id))
            is_book_in_cart = cur.fetchone()
            if is_book_in_cart is None:     #if book not in cart add it
                cur.execute("select book_price from book where id = %s", (book_id,))
                book_price = cur.fetchone()[0]
                cur.execute("""insert into `cart item` (cart_id, book_id , book_price) 
                            values (%s, %s, %s)""", (user_cart_id, book_id, book_price))
                mysql.connection.commit()
                cur.execute("""UPDATE `library_available_book` SET copies_no = copies_no - 1 
                            WHERE book_id = %s""" , (book_id,))
                mysql.connection.commit()
                cur.close()
                return jsonify({"message": "تمت إضافة الكتاب إلى السلة بنجاح"}) 
            else:       #if book in cart increase the number of copies
                cur.execute("""UPDATE `cart item` SET books_no = books_no + 1
                            WHERE book_id = %s and cart_id =%s """, (book_id, user_cart_id))
                mysql.connection.commit()
                cur.execute("""UPDATE `library_available_book` SET copies_no = copies_no - 1 
                            WHERE book_id = %s""" , (book_id,))
                mysql.connection.commit()
                cur.close()
                return jsonify({"message": "تمت زيادة نسخة من الكتاب إلى السلة بنجاح"})

    else:       #if user has a cart add the book to it 
        cur.execute("select id from cart where user_id = %s and status= %s", (user_id,'P' ))
        user_cart_id = cur.fetchone()[0]
        cur.execute("select copies_no from `library_available_book` where book_id =%s", (book_id,))
        copy_no = cur.fetchone()[0]
        if copy_no == 0:
            cur.close()
            return jsonify({"message": "لا يوجد نسخ متاحة حاليًا"})
        else:       #if there is a copy of the book in the library
            cur.execute("""select book_id from `cart item` where cart_id = %s and book_id = %s""", (user_cart_id, book_id))
            is_book_in_cart = cur.fetchone()
            if is_book_in_cart is None:
                cur.execute("select book_price from book where id = %s", (book_id,))
                book_price = cur.fetchone()[0]
                cur.execute("""insert into `cart item` (cart_id, book_id , book_price) 
                            values (%s, %s, %s)""", (user_cart_id, book_id, book_price))
                mysql.connection.commit()
                cur.execute("""UPDATE `library_available_book` SET copies_no = copies_no - 1 
                            WHERE book_id = %s""" , (book_id,))
                mysql.connection.commit()
                cur.close()
                return jsonify({"message": "تمت إضافة الكتاب إلى السلة بنجاح"})

            else:       #if book in cart increase the number of copies
                cur.execute("""UPDATE `cart item` SET books_no = books_no + 1
                            WHERE book_id = %s and cart_id =%s """, (book_id, user_cart_id))
                mysql.connection.commit()
                cur.execute("""UPDATE `library_available_book` SET copies_no = copies_no - 1 
                            WHERE book_id = %s""" , (book_id,))
                mysql.connection.commit()
                cur.close()
                return jsonify({"message": "تمت إضافة نسخة من الكتاب إلى السلة بنجاح"})

#function to show all items in cart (if user click on basket icon in the app)
@cart.route("/show_cart/<int:user_id>", methods=[ 'GET'])
def show_cart(user_id):
    cur = mysql.connection.cursor()
    cur.execute("select id from cart where user_id = %s and status= %s", (user_id, 'P'))
    result = cur.fetchone()     #check if user has a cart
    if (result) is None:    #if user doesn't has a cart create one 
        cur.execute("INSERT INTO cart (user_id,status) VALUES (%s,%s)", (user_id,"P"))
        mysql.connection.commit()
        cur.execute("select id from cart where user_id = %s", (user_id, ))
        user_cart_id = cur.fetchone()[0]
        cur.close()
        return [], 200

    else:   #if user has a cart show the items in it
        cur.execute("select id from cart where user_id = %s and status= %s", (user_id, 'P'))
        user_cart_id = cur.fetchone()[0]
        cur.execute(""" select `cart item`.book_price, book.book_name, 
                    `cart item`.books_no, book.image_url, book.id
                    from `cart item`
                    INNER JOIN book ON `cart item`.book_id = book.id
                    where `cart item`.cart_id = %s""", (user_cart_id,))
        query_return = cur.fetchall()
        books_in_cart = []
        for data in query_return:
            book_in_cart = {"book_price": int(data[0]), "book_name": data[1],
                                "copies_no": data[2], "image": data[3] , "book_id": data[4]}
            books_in_cart.append(book_in_cart)
        cur.close()
        return books_in_cart

#function to add a copy of a book to cart (if user click on plus icon basket page)
@cart.route("/add_copy", methods=['POST'])
def add_copy():
    
    data = request.get_json()
    print("data " , data)
    user_id = data['user_id']
    book_id = data['book_id']
    print("user_id " , user_id)
    print("book_id " , book_id)
    cur = mysql.connection.cursor()
    cur.execute("select copies_no from `library_available_book` where book_id =%s", (book_id,))
    copy_no = cur.fetchone()[0]
    if copy_no == 0:
        cur.close()
        return jsonify({"status": 0})
    else:
        cur.execute("select id from cart where user_id = %s and status = 'P'", (user_id, ))
        user_cart_id = cur.fetchone()[0]
        print("user_cart_id " , user_cart_id)
        cur.execute("""UPDATE `cart item` SET books_no = books_no + 1
                    WHERE book_id = %s and cart_id =%s """, (book_id, user_cart_id))
        mysql.connection.commit()

        cur.execute("""UPDATE `library_available_book` SET copies_no = copies_no - 1 
                    WHERE book_id = %s""" , (book_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"status": 1})
       

#function to remove a copy of a book to cart (if user click on minus icon basket page)
@cart.route("/remove_copy", methods=['POST'])
def remove_copy():
    data = request.get_json()
    user_id = data['user_id']
    book_id = data['book_id']
    cur = mysql.connection.cursor()
    cur.execute("select id from cart where user_id = %s and status= %s", (user_id,'P' ))
    user_cart_id = cur.fetchone()[0]
    cur.execute("""select books_no from `cart item` where book_id =%s and cart_id= %s""",(book_id,user_cart_id))
    copy_numbers = cur.fetchone()[0]
    if copy_numbers == 0:
        cur.close()
        return jsonify({"status": 0})
        
    else:
        cur.execute("""UPDATE `cart item` SET books_no = books_no - 1
                    WHERE book_id = %s and cart_id =%s """, (book_id, user_cart_id))
        mysql.connection.commit()
        cur.execute("""UPDATE `library_available_book` SET copies_no = copies_no + 1 
                    WHERE book_id = %s""" , (book_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"status": 1})
       
    
#function to create the order (if user click on okay button in basket page)
@cart.route("/create_order", methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = data['user_id']
    address = data['address']
    cur = mysql.connection.cursor()
    cur.execute("select id from cart where user_id = %s and status= %s", (user_id,'P' ))
    cart_id = cur.fetchone()[0]
     #handle if user already create order but cancel payment
    cur.execute("select id from orders where cart_id= %s and status = 'P'" , (cart_id,))
    response = cur.fetchall()
    if response == None:
        print("order already exists")
        cur.close()
        return jsonify({"status": 1})
    else:
        cur.execute("""insert into orders (user_id, address, cart_id) values (%s,%s,%s)""",
                    (user_id, address, cart_id))
        mysql.connection.commit()
        print("create order in orders table")
        cur.close()
        return jsonify({"status": 1})
    # cur.execute("""insert into orders (user_id, address, cart_id) values (%s,%s,%s)""",
    #             (user_id, address, cart_id))
    # mysql.connection.commit()
    # print("create order in orders table")
    # update cart status and delete cart item should handle when payment success
    # cur.execute("""UPDATE cart SET status = 'C'
    #                 WHERE user_id = %s and status = 'P'""", (user_id,))
    # mysql.connection.commit()
    # print("update status of the cart to C")
    
    # cur.execute("select id from orders where user_id = %s and status = 'P'", (user_id,))
    # order_id = cur.fetchone()[0]
    # cur.execute("select book_id , book_price , books_no from `cart item` where cart_id =%s", (cart_id,))
    # cart_items = cur.fetchall()
    # # print(f"cart items: {cart_items}")
    # list_of_items = []
    # for data in cart_items:
    #     item = {"book_id": data[0], "book_price": data[1], "copies_no": data[2]}
    #     list_of_items.append(item)
    # for item in list_of_items:
    #     cur.execute("""insert into `order items` (order_id, book_id, book_price, copies_no)
    #                 values (%s,%s,%s,%s)""", 
    #                 (order_id, item['book_id'], item['book_price'], item['copies_no']))
    #     mysql.connection.commit()
    # print(f"insert items from cart items table in order item table where order id = {order_id}")
    # cur.execute("""DELETE FROM  `cart item` WHERE cart_id =%s""",(cart_id,))
    # mysql.connection.commit()
    # print(f"delete items from cart items table with specific cart id {cart_id}")
#    ) cur.close()
#     return jsonify({"status": 1}

