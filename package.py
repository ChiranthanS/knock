from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
 
mysql = MySQL(app)

class Package():

    def __init__(self, user_id, sender_name, sender_mobile, sender_email, receiver_name, price, tracking, addr_to, addr_from):
        self.user_id = user_id
        self.sender_name = sender_name
        self.sender_mobile = sender_mobile
        self.sender_email = sender_email
        self.receiver_name = receiver_name
        self.price = price
        self.tracking = tracking
        self.addr_to = addr_to
        self.addr_from = addr_from

    def create(sender_name, sender_mobile, sender_email, receiver_name, price, tracking, addr_from, addr_to, service_type, user_id=None):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Create_Order', [user_id, sender_name, sender_mobile, sender_email, receiver_name, tracking,price,addr_from["street1"], addr_from["street2"], addr_from["city"], addr_from["state"], addr_from["zip"], addr_to["street1"], addr_to["street2"], addr_to["city"], addr_to["state"], addr_to["zip"], service_type])
        cursor.close()
        mysql.connection.commit()

    def get_location(tracking):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_location', [tracking])
        package = cursor.fetchone()
        cursor.close()

        if not package:
            return None

        addr_curr = {
            "line1": package['from_line1'],
            "line2": package['from_line2'],
            "city": package['from_city'],
            "state": package['from_state'],
            "zip": package['from_zip']
        }
        return addr_curr

    def set_location(tracking_id, addr):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Set_location', [tracking_id, addr["street1"], addr["street2"], addr["city"], addr["state"], addr["zip"]])
        user_details = cursor.fetchone()
        print(user_details)
        cursor.close()
        mysql.connection.commit()
        print(user_details)
        return user_details['sender_email']

    def get_status(tracking):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_status', [tracking])
        package = cursor.fetchone()
        cursor.close()

        if not package:
            return None
        
        return package['order_status']
    
    def set_status(tracking, status):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Set_status', [tracking,status])
        cursor.close()
        mysql.connection.commit()

    def get_orders():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_Orders')
        orders = cursor.fetchall()
        cursor.close()

        return orders

    def get_driver(tracking):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_Driver', [tracking])
        orders = cursor.fetchone()
        cursor.close()

        return orders

    def assign(order_id, driver_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Assign', [order_id, driver_id])
        cursor.close()
        mysql.connection.commit()

    def get_driver_orders(driver_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_Driver_Orders', [driver_id])
        orders = cursor.fetchall()
        cursor.close()

        return orders

    def get_order(order_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_Order', [order_id])
        order = cursor.fetchone()
        cursor.close()

        return order
