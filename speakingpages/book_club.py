from flask import  Blueprint, jsonify, request
from speakingpages import mysql


book_club = Blueprint("book_club", __name__)


@book_club.route("/relgious_clubs")
def relgious_clubs():
    cur = mysql.connection.cursor()
    cur.execute("""select club_name , club_level,club_duration,
                `book club admin`.name , subscription, `book club`.image_url, `book club`.id
                from `book club`
                INNER JOIN `book club admin` ON  
                `book club`.admin_id = `book club admin`.id
                where `book club`.club_field = 1
                """)
    result = cur.fetchall()
    clubs = []
    for data in result:
        club = {"club_name": data[0], "club_level": data[1],
                "club_duration": data[2], "admin_name": data[3], 
                 "subscription": data[4], "image_url": data[5], "club_id": data[6]}
        clubs.append(club)
    cur.close()
    return jsonify(clubs)

@book_club.route("/cultural_clubs")
def cultural_clubs():
    cur = mysql.connection.cursor()
    cur.execute("""select club_name , club_level,club_duration,
                `book club admin`.name , subscription, `book club`.image_url, `book club`.id
                from `book club`
                INNER JOIN `book club admin` ON  
                `book club`.admin_id = `book club admin`.id
                where `book club`.club_field = 2
                """)
    result = cur.fetchall()
    clubs = []
    for data in result:
        club = {"club_name": data[0], "club_level": data[1],
                "club_duration": data[2], "admin_name": data[3], 
                 "subscription": data[4], "image_url": data[5], "club_id": data[6]}
        clubs.append(club)
    cur.close()
    return jsonify(clubs)

@book_club.route("/literature_clubs")
def literature_clubs():
    cur = mysql.connection.cursor()
    cur.execute("""select club_name , club_level,club_duration,
                `book club admin`.name , subscription, `book club`.image_url, `book club`.id
                from `book club`
                INNER JOIN `book club admin` ON  
                `book club`.admin_id = `book club admin`.id
                where `book club`.club_field = 3
                """)
    result = cur.fetchall()
    clubs = []
    for data in result:
        club = {"club_name": data[0], "club_level": data[1],
                "club_duration": data[2], "admin_name": data[3], 
                 "subscription": data[4], "image_url": data[5], "club_id": data[6]}
        clubs.append(club)
    cur.close()
    return jsonify(clubs)

#check if user is member in certain club or not
@book_club.route("/club_member", methods=['POST'])
def club_member():
    data = request.get_json()
    print("club member: ", data)
    user_id = data['user_id']
    club_id = data['club_id']
    cur = mysql.connection.cursor()
    cur.execute("""select * from `book club member` 
                where user_id = %s and club_id = %s""" ,(user_id, club_id))
    is_user_member = cur.fetchall()
    if is_user_member == None:
        cur.close()
        return jsonify({"status": 0})
    else:
        cur.close()
        return jsonify({"status":1})
