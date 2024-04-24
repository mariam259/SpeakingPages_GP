from flask import Blueprint, jsonify, request
import stripe
from speakingpages import mysql

payment = Blueprint('payment', __name__)

STRIPE_PUBLIC_KEY = 'pk_test_51OnsGPFcaomoWuq20p8mcEPHx2uYUIr0Ay8oGbD1K2juNxZnxbL2NbWMM3EWzfAmhcLjy9AE29iNaiu6irP21FiE00QnPokeIv'
STRIPE_SECRET_KEY = 'sk_test_51OnsGPFcaomoWuq2X3mUJC7vp0t5F6kwsM5T3WcsoHnm9qVLrpkIBKPSFH4EP6DmMs2M69ztKbr07Q2ATANc74Pi00QwJQrhYA'
stripe.api_key = STRIPE_SECRET_KEY


# Get the total price for the order
def get_total(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""select id from cart where user_id= %s and status = 'P'""", 
                (user_id,))
    cart_id = cur.fetchone()[0]
    cur.execute("""select cart_id ,SUM(book_price* books_no) as total_invoice
                from `cart item`
                inner join cart on `cart item`.cart_id = cart.id
                where cart.status = 'P' and `cart item`.cart_id = %s
                group by cart_id""", (cart_id,))
    items = cur.fetchall()
    print("items: ", items)
    # data_items = {"}
    total_data = {"order_id": items[0][0], 
                  "total_invoice": items[0][1]}
    total = items[0][1]
    cur.close()
    return total

# Check if a customer exists based on email
def does_customer_exist(email):
    try:
        # Search for customers based on email
        customers = stripe.Customer.list(
            email=email,
            limit=1  # Limit search to 1 customer
        )
        # Check if any customers found
        return len(customers.data) > 0
    except Exception as e:
        print("Error in find customer by email: ", e)
        return False


def get_customer_by_email(email):
    customers = stripe.Customer.list(limit=50)  # Adjust limit as needed
    for customer in customers.auto_paging_iter():
        if customer.email == email:
            return customer

def get_user_id(customer_id):
    cur = mysql.connection.cursor()
    cur.execute("""select id from user where customer_id = %s""", 
                (customer_id,))
    user_id = cur.fetchone()[0]
    cur.close()
    return user_id





@payment.route('/book_payment_sheet', methods=['POST'])
def payment_sheet():
    cur = mysql.connection.cursor()
    event = stripe.Event.construct_from(
        request.json,
        stripe.api_key
    )
    if event.type == 'payment_intent.created':
        print('payment intent created' )
        return jsonify({'success': "payment intent created"})
    
    elif event.type == 'payment_intent.canceled':
        print('payment intent canceled')
        return jsonify({'status': False , 'error': "payment intent canceled"})
    
    elif event.type == 'checkout.session.completed':
        session = event.data.object
        print("checkout session: ", session)
        return jsonify({'success': True}), 200
    
    elif event.type == 'payment_intent.payment_failed':
        print('payment intent failed')
        return jsonify({'success': False , 'error': "payment intent failed"})
    
    elif event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        if (payment_intent.metadata.get("for") == "club"):
            user_id = int(payment_intent.metadata["user_id"])
            club_id = int(payment_intent.metadata["club_id"])
            cur.execute("""insert into `book club member` (user_id , club_id) values (%s, %s)""", 
                (user_id, club_id))
            mysql.connection.commit()
            cur.close()
            print('payment intent for book club succedded')
            return jsonify({'success': True}), 200
        else:
            customer_id = payment_intent.customer
            user_id = get_user_id(customer_id)
            # update cart status from P to C
            cur.execute("select id from cart where user_id = %s and status= %s", (user_id,'P' ))
            cart_id = cur.fetchone()[0]

              
            cur.execute("select id from orders where user_id = %s and status = 'P'", (user_id,))
            order_id = cur.fetchone()[0]

            cur.execute("""UPDATE cart SET status = 'C'
                          WHERE user_id = %s and status = 'P'""", (user_id,))
            mysql.connection.commit()
            print("update status of the cart in payment to C")
            
            cur.execute("select book_id , book_price , books_no from `cart item` where cart_id = %s", (cart_id,))
            cart_items = cur.fetchall()
            # print(f"cart items: {cart_items}")
            list_of_items = []
            for data in cart_items:
                item = {"book_id": data[0], "book_price": data[1], "copies_no": data[2]}
                list_of_items.append(item)
            for item in list_of_items:
                cur.execute("""insert into `order items` (order_id, book_id, book_price, copies_no)
                            values (%s,%s,%s,%s)""", 
                            (order_id, item['book_id'], item['book_price'], item['copies_no']))
                mysql.connection.commit()
            print(f"insert items from cart items table in order item table where order id = {order_id}")
            cur.execute("""DELETE FROM  `cart item` WHERE cart_id =%s""",(cart_id,))
            mysql.connection.commit()
            print(f"delete items from cart items table with specific cart id {cart_id}")

            cur.execute("""UPDATE orders SET status = 'C' WHERE status = 'P' and user_id = %s""",
                        (user_id,))
            mysql.connection.commit()
            # cur.execute("""DELETE FROM cart WHERE id =%s""",(cart_id,))
            # mysql.connection.commit()
            # print(f"delete cart with id: {cart_id}")
            print('payment intent for books succedded')
            cur.close()
            return jsonify({'success': True}), 200
    
    elif event.type == payment_intent.processing:
        print('payment intent processing')
        return jsonify({'success': True}), 200
    
    
    




@payment.route('/payment_intent', methods=['POST'])
def payment_intent():
    # Use an existing Customer ID if this is a returning customer
    customer_data = request.get_json()
    print("this is customer data: ",customer_data)
    id = customer_data['id']
    cur = mysql.connection.cursor()
    # Extract relevant data from request
    cur.execute("""select first_name, email, orders.address
                from user 
                inner join orders on user.id = orders.user_id
                where user.id = %s""", (id,))
    user_data = cur.fetchall()
    user = {'name': user_data[0][0], 
                    'email': user_data[0][1], 'address': user_data[0][2]}
    print("user: ", user)
    user_email=str(user['email'])
    user_name=str(user['name'])
    user_address=user['address']

    # Check if customer exists
    if does_customer_exist(user_email):
        customer = get_customer_by_email(user_email)
    else:
        # Create customer object
        customer = stripe.Customer.create(
            email=user_email,
            name=user_name,
            address = {'line1':user_address, "country": "Egypt"}  
        )
    cur.execute("""UPDATE user SET customer_id = %s WHERE id = %s """,
                (customer.id, id))
    mysql.connection.commit()
    ephemeralKey = stripe.EphemeralKey.create(
                customer=customer['id'],
                stripe_version='2023-10-16',
        )
    total = int(get_total(id))
    paymentIntent = stripe.PaymentIntent.create(
        amount= int(total * 100 + (30*100)),
        currency="egp",
        customer= customer['id'],
        # metadata= {"user_id": id , "for": "books"},
        # In the latest version of the API, specifying the `automatic_payment_methods` parameter
        # is optional because Stripe enables its functionality by default.
        automatic_payment_methods = {
        'enabled': True,
            } ,
    )
    cur.close()
    return jsonify( {'paymentIntent': paymentIntent.client_secret,
        "ephemeralKey" :ephemeralKey.secret,
        "customer" : customer.id,
        "publishableKey":STRIPE_PUBLIC_KEY}),200


@payment.route('/club_payment_intent', methods=['POST'])
def club_payment_intent():
    data = request.get_json()
    print("this is club data: ",data)
    user_id = data['id']
    club_id = data['clubId']
    cur = mysql.connection.cursor()
    cur.execute("""select first_name, email
                from user 
                where user.id = %s""", (user_id,))
    user_data = cur.fetchall()
    user = {'name': user_data[0][0], 
                    'email': user_data[0][1]}
    print("user: ", user)
    user_email=str(user['email'])
    user_name=str(user['name'])

    # Check if customer exists
    if does_customer_exist(user_email):
        customer = get_customer_by_email(user_email)
    else:
        # Create customer object
        customer = stripe.Customer.create(
            email=user_email,
            name=user_name,
            address = {"country": "Egypt"}  
        )
    cur.execute("""UPDATE user SET customer_id = %s WHERE id = %s """,
                (customer.id, user_id))
    mysql.connection.commit()
    ephemeralKey = stripe.EphemeralKey.create(
                customer=customer['id'],
                stripe_version='2023-10-16',
                )
    paymentIntent = stripe.PaymentIntent.create(
        amount= 200 * 100,
        currency="egp",
        customer= customer['id'],
        metadata={"for": "club" , "club_id": club_id , "user_id": user_id},
    # In the latest version of the API, specifying the `automatic_payment_methods` parameter
    # is optional because Stripe enables its functionality by default.
        automatic_payment_methods = {
        'enabled': True,
            } ,
        # locals= 'ar'
    )
    # cur.execute("""insert into `book club member` 
    #             (user_id , club_id) values (%s, %s)""", 
    #             (user_id, club_id))
    # mysql.connection.commit()
    cur.close()
    print("this is metadata: ", paymentIntent.metadata)
    return jsonify( {'paymentIntent': paymentIntent.client_secret,
        "ephemeralKey" :ephemeralKey.secret,
        "customer" : customer.id,
        "publishableKey":STRIPE_PUBLIC_KEY}),200
           








# Replace this endpoint secret with your endpoint's unique secret
# If you are testing with the CLI, find the secret by running 'stripe listen'
# If you are using an endpoint defined with the API or dashboard, look in your webhook settings
# at https://dashboard.stripe.com/webhooks

# @payment.route('/webhook', methods=['POST'])
# def webhook():
#     event = stripe.Event.construct_from(
#         request.json,
#         stripe.api_key
#     )
#     if event.type == 'payment_intent.created':
#         payment_intent = event.data.object
#         print('payment intent created' )
#     if event.type == 'payment_intent.canceled':
#         print('payment intent canceled')
#     if event.type == 'checkout.session.completed':
#         session = event.data.object
#         print("checkout session: ", session)
#     return jsonify({'status': 'success'}), 200

