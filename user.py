from flask import Flask
from flask_login import UserMixin
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
 
mysql = MySQL(app)

class User(UserMixin):
    def __init__(self, id_, name, email, user_type, H_pass, Google_id,security_question,security_answer):
        self.id = id_
        self.name = name
        self.email = email
        self.user_type = user_type
        self.H_pass = H_pass
        self.Google_id = Google_id
        self.security_question = security_question 
        self.security_answer = security_answer 

    @staticmethod
    def check(login_email):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Check_Email', [login_email])
        userdetails = cursor.fetchone()
        cursor.close()

        if not userdetails:
            return None
        user = User(
            id_=userdetails["user_id"], 
            name=userdetails["user_name"], 
            email=login_email, 
            user_type=userdetails["user_type_id"], 
            H_pass=userdetails["user_passkey"], 
            Google_id=userdetails["Google_id"],
            security_question=userdetails["Question"],
            security_answer=userdetails["Security_ans"]
        )
        return user

    @staticmethod
    def create(user_type, name, email, H_pass, mobile=None, addr1=None, city=None, state=None, zip=None,security_question=None, security_answer=None, Google_id=0):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        print ("Security details: ",security_question, security_answer)
        q_id = 0
        if security_question == "What is your mother's maiden name?":
            q_id=1
        elif security_question == "What is the name of your first pet?":
            q_id=2
        elif security_question == "What is your favorite book?":
            q_id=3
        cursor.callproc('Create_New_User', [user_type,name, email,H_pass, mobile, addr1, city, state, zip, Google_id,q_id, security_answer])
        cursor.close()
        mysql.connection.commit()

    @staticmethod
    def get(user_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_User', [user_id])
        userdetails = cursor.fetchone()
        cursor.close()
        if not userdetails:
            return None
        user = User(
            id_=user_id, 
            name=userdetails["user_name"], 
            email=userdetails["email"], 
            user_type=userdetails["user_type_id"], 
            H_pass=userdetails["user_passkey"], 
            Google_id=userdetails["Google_id"],
            security_question=userdetails["Question"],
            security_answer=userdetails["Security_ans"]
        )
        return user


    def saveMobile(user_id, mobile):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Update_Mobile', [user_id, mobile])
        cursor.close()
        mysql.connection.commit()

    def saveAddr(user_id, addr1, city, state, zip, addr2=None):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Update_Address', [user_id, addr1, addr2, city, state, zip])
        cursor.close()
        mysql.connection.commit()

    def getAddr(user_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_Address', [user_id])
        userdetails = cursor.fetchone()
        cursor.close()

        return userdetails
    
    def getDrivers():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_Drivers')
        drivers = cursor.fetchall()
        cursor.close()

        return drivers

    def getAdmins():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_Admins')
        admins = cursor.fetchall()
        cursor.close()

        return admins

    def getCustomers():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_Customers')
        customers = cursor.fetchall()
        cursor.close()

        return customers
    
    def getForgotMobile(login_email):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Get_MobilewithEmail', [login_email])
        userdetails = cursor.fetchone()
        cursor.close()
        if not userdetails:
            return None
        return (userdetails["mobile"], userdetails["Question"], userdetails["Security_ans"]) #added security question and answer
    
    #new resetPassword method
    def resetPassword(email, H_pass):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('Reset_Password', [email,H_pass])
        cursor.close()
        mysql.connection.commit()
