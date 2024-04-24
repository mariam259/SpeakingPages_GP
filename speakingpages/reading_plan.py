from flask import  Blueprint, jsonify, request
from speakingpages import mysql
from datetime import datetime
reading_plan = Blueprint('reading_plan', __name__)


@reading_plan.route('/create_reading_plan', methods=['POST'])
def create_reading_plan():
    data = request.get_json()
    user_id = data['user_id']
    book_name = data['book_name']
    start_date =  datetime.strptime(data["start_date"],'%b %d, %Y %I:%M:%S %p').date()
    print(start_date)
    end_date= datetime.strptime(data["end_date"],'%b %d, %Y %I:%M:%S %p').date()
    print("end_date", end_date)
    hours = data['hours']
    pages_no = data['pages_no']
    number_of_days = (end_date - start_date).days
    pages_per_day = pages_no / number_of_days
    cur = mysql.connection.cursor()
    cur.execute("""insert into `reading plan` (user_id , book_name, start_date, finish_date, 
                    pages_no, available_hours,days_number, pages_per_day )
                    values(%s, %s, %s, %s, %s, %s,%s, %s)""",
                 (user_id, book_name, start_date, end_date, pages_no, 
                  hours,number_of_days, pages_per_day))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message":"reading plan created successfully", "status":1})


@reading_plan.route('/show_reading_plan/<int:user_id>', methods = ['GET'])
def show_reading_plan(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""select book_name , pages_per_day, days_number, start_date ,
                 finish_date from `reading plan` where user_id = %s""", (user_id,))
    reading_plan_data = cur.fetchall()
    reading_plans = []
    for data in reading_plan_data:
        if int(data[1]) == 0:
            reading_plans.append({'book_name': data[0], 'pages_per_day': 1,
                              'days_number':int(data[2]),
                              'start_date':data[3].strftime("%Y-%m-%d"), 
                              'end_date': data[4].strftime("%Y-%m-%d")})
        else:
            reading_plans.append({'book_name': data[0], 'pages_per_day': int(data[1]),
                              'days_number':int(data[2]),
                              'start_date':data[3].strftime("%Y-%m-%d"), 
                              'end_date': data[4].strftime("%Y-%m-%d")})
    cur.close()
    return jsonify(reading_plans)