from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
 
mysql = MySQL(app)

class Chat():

    def __init__(self, user_name, room_id, message, time):
        self.user_name = user_name
        self.room_id = room_id
        self.message = message
        self.time = time

    def add(user_name, room_id, message, time):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Add_Message', [user_name, room_id, message, time])
        cursor.close()
        mysql.connection.commit()

    def get_room_history(room_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Room_History', [room_id])
        history = cursor.fetchall()
        cursor.close()

        return history

    def add_notifs(sender_name, sender_id, receiver_id, room_id = None):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Add_Notifs', [sender_name, sender_id, receiver_id, room_id])
        cursor.close()
        mysql.connection.commit()

    def get_notifs(receiver_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_Notifs', [receiver_id])
        notifs = cursor.fetchall()
        cursor.close()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Remove_Notifs', [receiver_id])
        cursor.close()
        mysql.connection.commit()

        return notifs

    def remove_notifs(receiver_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Remove_Notifs', [receiver_id])
        cursor.close()
        mysql.connection.commit()