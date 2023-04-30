from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
 
mysql = MySQL(app)

class Review():

    def __init__(self, order_id, service, rating, comment):
        self.order_id = order_id
        self.service = service
        self.rating = rating
        self.comment = comment

    def create(order_id, service, rating, comment):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Submit_Review', [order_id, service, rating, comment])
        cursor.close()
        mysql.connection.commit()

    def get_reviews():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_Reviews')
        reviews = cursor.fetchall()
        cursor.close()

        return reviews
