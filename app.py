import os
from http import cookies #storing the email for forgot password
import json
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_bcrypt import generate_password_hash, check_password_hash
# use pip install -I flask-googlemaps==0.4.0 for this
from flask_googlemaps import GoogleMaps, Map 
from oauthlib.oauth2 import WebApplicationClient
import requests
import re
import configparser
from package import Package
from review import Review
from user import User
from chat import Chat
import shippo
from flask import *
import random 
from geopy.geocoders import Nominatim
from flask_socketio import SocketIO, emit, join_room, disconnect
from datetime import datetime
# from flask_mail import Mail, Message

app = Flask(__name__)
cookie = cookies.SimpleCookie()

app.config['MYSQL_HOST'] = '35.226.141.189'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'knock_knock'

mysql = MySQL(app)
 
## From https://www.geeksforgeeks.org/login-and-registration-project-using-flask-and-mysql/
## Google log in from https://realpython.com/flask-google-login/ 

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configuration
config = configparser.ConfigParser()
config.read('config.cfg')
google_client_id = config.get('GOOGLE', 'GOOGLE_CLIENT_ID')
google_client_secret = config.get('GOOGLE', 'GOOGLE_CLIENT_SECRET')
shipping_client_key = config.get('SHIPPING', 'CLIENT_KEY')
map_key = config.get('MAP', 'MAP_KEY')

# Input credentials
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", google_client_id)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", google_client_secret)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

shippo.config.api_key = shipping_client_key

GoogleMaps(app, key=map_key)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

socketio = SocketIO(app)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    if user:
        return user
    
    else:
        return None

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('home'))

@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        user = User.get(user_id)
        id = user.user_type
        name = user.name

        messages = Chat.get_notifs(user_id)
        if messages:
            for message in messages:
                if message['room_id'] == str(0):
                    flash("New message from drivers group chat")
                else:
                    flash("New message from " + message['sender_name'])
            return redirect(url_for('home'))

        if id == 1:
            return render_template('admin_index.html', name=name, id=user_id)
        elif id == 2:
            return render_template('driver_index.html', name=name, id=user_id)
        elif id == 3:
            return render_template('index.html', name=name, id=user_id)
        # return (render_template('index.html', name = current_user.name))
        # return (render_template('login1.html', name = current_user.name))
    else:
        msg = ''

        if request.method == 'POST':
            user_type = request.form['type'] 
            user_type_id = toUserID(user_type)
            email = request.form['email']
            password = request.form['password']

            if not email or not password:
                msg = 'Incorrect username / password !'
                return render_template('login.html', msg = msg)

            # Retrieves user from DB
            user = User.check(email)

            # If nothing is returned
            if user.Google_id == "1":
                msg = 'Login through Google with this email'
                return render_template('login.html', msg = msg)
            elif not user or not check_password_hash(user.H_pass, password):
                msg = 'Incorrect username / password!'
                return render_template('login.html', msg = msg)
            elif user_type_id != user.user_type:
                msg = 'User type doesn\'t match account'
                return render_template('login.html', msg = msg)
            else: # else logs in user
                login_user(user)
                if user_type_id == 1:
                    return render_template('admin_index.html', name=user.name, id=user.id)
                elif user_type_id == 2:
                    return render_template('driver_index.html', name=user.name, id=user.id)
                elif user_type_id == 3:
                    return render_template('index.html', name=user.name, id=user.id)
                # return render_template('login1.html', name = user.name)
        print("Get of home called")
        return render_template('login.html')
    

################## Two Factor authentication ####################
app.secret_key = 'otp'

@app.route('/getOTP', methods = ['POST'])
def getOTP():
    email = request.form['email'] 

    user = User.check(email)

    if not user:
        return render_template('login.html', msg="Email address does not exist!")

    elif int(user.Google_id) == 1:
        return render_template('login.html', msg="Cannot reset Google email password")
    
    elif user!=None:

        cookie['email'] = email #email stored in cookie

        mobile_number, security_question, security_answer = User.getForgotMobile(email)
        cookie['security_question'] = security_question #storing security question 
        cookie['security_answer'] = security_answer #storing security answer

        #val = getOTPApi(User.getForgotMobile(email))
        val = getOTPmail(email)

        if val:
            #return render_template('enterOTP.html')
            return render_template('enterOTP.html', email=email)
        else:
            return render_template('login.html', msg="Couldn't verify account")
    

@app.route('/validateOTP', methods = ['POST'])
def validateOTP():
    otp = request.form['otp']
    if 'response' in session:
        s = session['response']
        session.pop('response', None)
        if s == otp:
            return render_template('reset_password.html')
        else:
            return render_template('login.html', msg="Couldn't verify account")

def send_email_confirmation(user_email, tracking):
    #app = Flask(__name__)
    mail= Mail(app)

    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'knockknock.deliveryservices@gmail.com'
    app.config['MAIL_PASSWORD'] = 'vagd posz cxia qzai'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    #email = User.getEmailFromTrackingID(tracking_id)

    mail = Mail(app)
    msg = Message('Knock Knock Delivery Status Update', sender = 'knockknock.deliveryservices@gmail.com', recipients = [user_email])
    msg.body = "Hey! your package location has been updated for the tracking id" + str(tracking)
    mail.send(msg)
    print("Email Sent !")        

def generateOTP():
    return random.randrange(100000, 999999)

def getOTPmail(user_email):
    otp = generateOTP()
    session['response'] = str(otp)
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'knockknock.deliveryservices@gmail.com'
    app.config['MAIL_PASSWORD'] = 'vagd posz cxia qzai'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    #email = User.getEmailFromTrackingID(tracking_id)

    otpmail = Mail(app)
    msg = Message('Knock Knock Delivery Reset Password', sender = 'knockknock.deliveryservices@gmail.com', recipients = [user_email])
    msg.body = "Hey! Please use this OTP to reset your password : " + str(otp)
    otpmail.send(msg)
    print("OTP Email Sent !")

    return True

@app.route("/pass_reset", methods = ["POST","GET"])
def pass_reset():
    return render_template('login1.html')

@app.route("/confirm_password", methods = ["POST","GET"])
def confirm_password():
    reset_email = cookie['email'].value #### changes for saving the email cookie value
    security_question_backend = cookie['security_question'].value
    security_answer_backend = cookie['security_answer'].value
    cookie['email'] = '' #storing the email
    cookie['security_question'] = '' #storing the security question
    cookie['security_answer'] = '' #storing the security answer

############## Security question and answer logic ##################

#    id = User.getIdFromEmail(reset_email)
    print("id hereeee: ",id)

    password = request.form['password'] 
    print("password:", password)

    security_question = request.form['security-question1']
    print("security question:", security_question, " security_question_backend:", security_question_backend)

    security_answer = request.form['security-answer1']
    print("security answer:", security_answer, " security_answer_backend:", security_answer_backend)
    print(security_question,security_question_backend)
    if((security_question) == (security_question_backend)) and (security_answer == security_answer_backend):
        H_pass = generate_password_hash(password)
        User.resetPassword(reset_email,H_pass)
        return render_template('login.html')

    else:
        return render_template('reset_password.html', msg = "Security question and answer does not match")

###########################################

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        user_type = request.form['type']
        user_type_id = toUserID(user_type)
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        mobile = request.form['mobile']
        address_line1 = request.form['address_line1']
        city = request.form['city']
        state = request.form['state']
        zip = request.form['zip']
        security_question = request.form['security-question1']
        security_answer = request.form['security-answer1']
        H_pass = generate_password_hash(password)

        if not name or not password or not email or not mobile:
            msg = 'Please fill out the form!'
            return render_template('register.html', msg = msg)

        # For checking if user exists already
        user = User.check(email)

        if user:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        
        else:
            # Makes new user and logs it in
            User.create(user_type_id, name, email, H_pass, mobile, address_line1, city, state, zip,security_question,security_answer)
            user = User.check(email)
            login_user(user)
            return redirect(url_for('home'))
    
    return render_template('register.html', msg = msg)

@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User.check(users_email)

    # Doesn't exist? Add to database
    if not user:
        H_pass = generate_password_hash("google")
        User.create(user_type=3, name=users_name, email=users_email, H_pass=H_pass, Google_id=1, security_question=0, security_answer=0)
        user = User.check(users_email)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for('home')) 

@app.route('/search', methods=['GET', 'POST'])
def search():
    msg = ''
    if request.method == 'POST':
        # Collects input from user
        street1_to = request.form['street1_to']
        street2_to = request.form['street2_to']
        city_to = request.form['city_to']
        state_to = request.form['state_to']
        zip_to = request.form['zip_to']

        street1_from = request.form['street1_from']
        street2_from = request.form['street2_from']
        city_from = request.form['city_from']
        state_from = request.form['state_from']
        zip_from = request.form['zip_from']

        length = request.form['length']
        width = request.form['width']
        height = request.form['height']
        weight = request.form['weight']

        useFrom = request.form.get('useFrom')

        if useFrom and current_user.is_authenticated:
            user_id = current_user.get_id()
            user = User.getAddr(user_id)

            if user['address_line1'] == None or user['city'] == None or user['state'] == None or user['zip'] == None:
                msg = "No address saved to account"
                return render_template('search.html', msg = msg)

            street1_from = user['address_line1']
            street2_from = user['address_line2']
            city_from = user['city']
            state_from = user['state']
            zip_from = user['zip']

        # Check if form is filled out
        if not street1_to or not city_to or not state_to or not zip_to:
            msg = 'Invalid shipping location'
        elif not street1_from or not city_from or not state_from or not zip_from:
            msg = 'Invalid return location'
        elif not length or not width or not height or not weight:
            msg = 'Missing package information'
        # Checks if package size is a number
        elif not re.match(r'[0-9]+', length) or not re.match(r'[0-9]+', width) or not re.match(r'[0-9]+', height) or not re.match(r'[0-9]+', weight):
            msg = 'Package size and weight must be numbers'
        else:
            # Creates the send to address
            address_to = shippo.Address.create(
                street1 = street1_to,
                street2 = street2_to,
                city = city_to,
                state = state_to,
                zip = zip_to,
                country = "US",
                validate = True
            )

            # Creates the return address
            address_from = shippo.Address.create(
                street1 = street1_from,
                street2 = street2_from,
                city = city_from,
                state = state_from,
                zip = zip_from,
                country = "US",
                validate = True
            )

            # For validation of address
            validate_to = address_to.get('validation_results')
            validate_from = address_from.get('validation_results')

            if not validate_to['is_valid'] and not validate_from['is_valid']:
                msg = 'Return address and send to address is invalid'
                return render_template('search.html', msg = msg)
            elif not validate_to['is_valid']:
                msg = 'Address to send to is invalid'
                return render_template('search.html', msg = msg)
            elif not validate_from['is_valid']:
                msg = 'Return address is invalid'
                return render_template('search.html', msg = msg)
            elif street1_to == street1_from and city_to == city_from and state_to == state_from and zip_to == zip_from:
                msg = 'Addresses need to be the different'
                return render_template('search.html', msg = msg)
            
            session['addrto'] = address_to
            session['addrfrom'] = address_from

            saveFrom = request.form.get('saveFrom')

            if saveFrom and current_user.is_authenticated:
                user_id = current_user.get_id()
                User.saveAddr(user_id, address_from["street1"], address_from["city"], address_from["state"], address_from["zip"], address_from["street2"])

            # Creates parcel info for shipping
            parcel = {
                "length": length,
                "width": width,
                "height": height,
                # Distance units can be cm, in, ft, mm, m, yd
                "distance_unit": request.form['dist_units'],
                "weight": weight,
                # Mass units can be g, oz, lb, kg
                "mass_unit": request.form['mass_units']
            }

            # Creates shipments
            shipment = shippo.Shipment.create(
                address_from=address_from,
                address_to=address_to,
                parcels=[parcel],
                asynchronous=False
            )

            # Gets list of rates
            rates = shipment.rates

            # Finds the recommended rate and save it in session
            for rate in rates:
                if rate['servicelevel'] != []:
                    rate['servicelevel'] = rate['servicelevel']['name']
                
                if 'BESTVALUE' in rate['attributes']:
                    session['best'] = rate
                    session['orgbest'] = rate

            # Sends rates to be able to be used in html
            session['rates'] = rates
            session['original'] = rates

            return redirect(url_for('results'))
    elif request.method == 'POST':
        msg = 'Please fill out the form'
    return render_template('search.html', msg = msg)

@app.route('/search/filters', methods=['GET', 'POST'])
def filters():
    # Rates from search
    rates = session.pop('rates', [])
    # Will be the rates returned after searching
    filtered = []

    # Gets checkbox-returns true is checkbox is marked
    ups = request.form.get('ups')
    fedex = request.form.get('fedex')
    usps = request.form.get('usps')
    less10 = request.form.get('less10')
    tento20 = request.form.get('10to20')
    less3 = request.form.get('less3')
    threeto6 = request.form.get('3to6')

    # All of this is for the filter
    if ups:
        f = list(filter(check_ups, rates))
        filtered += f

    if usps:
        f = list(filter(check_usps, rates))
        filtered += f
    
    if fedex:
        f = list(filter(check_fedex, rates))
        filtered += f

    if less10 and not filtered:
        filtered = list(filter(check_less10, rates))
    elif less10 and filtered:
        filtered = list(filter(check_less10, filtered))

    if tento20 and not filtered:
        filtered = list(filter(check_10to20, rates))
    elif tento20 and filtered:
        filtered = list(filter(check_10to20, filtered))

    if less3 and not filtered:
        filtered = list(filter(check_less3, rates))
    elif less3 and filtered:
        filtered = list(filter(check_less3, filtered))
    
    if threeto6 and not filtered:
        filtered = list(filter(check_3to6, rates))
    elif threeto6 and filtered:
        filtered = list(filter(check_3to6, filtered))

    # If no, filter, return the results from search
    if not filtered:
        filtered = rates

    session['rates'] = filtered

    return redirect(url_for('results'))

def check_ups(rate):
    if rate['provider'] == 'UPS':
        return True
    
    return False

def check_fedex(rate):
    if rate['provider'] == 'FedEx':
        return True
    
    return False

def check_usps(rate):
    if rate['provider'] == 'USPS':
        return True
    
    return False

def check_less10(rate):
    if float(rate['amount']) < 10:
        return True
    
    return False

def check_10to20(rate):
    if float(rate['amount']) >= 10 and float(rate['amount']) < 20:
        return True
    
    return False

def check_less3(rate):
    if float(rate['estimated_days']) < 3:
        return True
    
    return False

def check_3to6(rate):
    if float(rate['estimated_days']) >= 3 and float(rate['estimated_days']) < 6:
        return True
    
    return False

@app.route('/search/results', methods=['GET', 'POST'])
def results():
    return render_template('results.html')

@app.route('/search/results/reset', methods=['GET', 'POST'])
def reset():
    # Original saves the search result that happened first, so this resets 
    # the rate to what it originally was
    session['rates'] = session['original']
    session['best'] = session['orgbest']

    return render_template('results.html')

@app.route('/payment/<service>/<id>/<price>', methods=['GET', 'POST'])
def payment(service, id, price):
    if request.method == "POST":
        # Gets info from form
        sender_name = request.form.get('sender_name')
        sender_mobile = request.form.get('sender_mobile')
        sender_email = request.form.get('sender_email')
        recv_name = request.form.get('recv_name')

        # Checks if form is filled out
        if not sender_email or not sender_name or not sender_mobile or not recv_name:
            return render_template('payment.html', service=service, id=id, price=price)

        # Get address info from session
        address_to = session.pop('addrto', [])
        address_from = session.pop('addrfrom', [])

        if not address_from or not address_to:
            return redirect(url_for('search'))

        # Get user id from the current session
        if current_user.is_authenticated:
            user_id = current_user.get_id()

        # Create the package, adds to database
        Package.create(sender_name, sender_mobile, sender_email, recv_name, price, id, address_from, address_to, service, user_id)

        return render_template('confirmation.html', id=id)

    return render_template('payment.html', service=service, id=id, price=price)

@app.route('/status/<id>', methods=['GET', 'POST'])
def status(id):
    # Gets current location and status of package
    location = Package.get_location(id)
    status = Package.get_status(id)

    if not location:
        return redirect(url_for('home'))

    # For getting latitude and longitude of city and state
    geolocator = Nominatim(user_agent='my_user_agent')

    city = location['city']
    state = location['state']

    loc = geolocator.geocode(city + ', ' + state + ', ' + 'US', timeout=10000)

    # Creates map
    map = Map(
        identifier="view-side",
        lat=loc.latitude,
        lng=loc.longitude,
        zoom=11
    )

    # If there's no location or status, there is no package, return home
    if not location or not status:
        return redirect(url_for('home'))

    return render_template('status.html', location = location, status = status, lat = loc.latitude, long = loc.longitude, map = map)

@app.route('/tracking', methods=['GET', 'POST'])
def tracking():
    # Retrieve tracking number from form
    tracking = request.form['tracking']

    # If nothing was inputted, return home
    if not tracking:
        return redirect(url_for('home'))

    return redirect(url_for('status', id=tracking))

@app.route('/assign', methods=['GET', 'POST'])
@login_required
def assign():
    user_id = current_user.get_id()
    messages = Chat.get_notifs(user_id)
    if messages:
        for message in messages:
            if message['room_id'] == str(0):
                flash("New message from drivers group chat")
            else:
                flash("New message from " + message['sender_name'])
        return redirect(url_for('assign'))

    drivers = User.getDrivers()
    orders = Package.get_orders()
    unassigned = list(filter(get_unassigned, orders))
    # Populates the page
    if request.method == 'GET':
        
        return render_template('assign.html', drivers = drivers, orders = unassigned)

    # Assigns order to driver
    if request.method == 'POST':
        driver = request.form.get('drivers')
        order = request.args.get('id', '')

        if driver:
            Package.assign(order, driver)

        unassigned = list(filter(get_unassigned, orders))

        return redirect(url_for('assign'))
        
@app.route('/drivers', methods=['GET', 'POST'])
@login_required
def drivers():
    # Show list of drivers
    # Can search based on name, id, transaction id, location
    # Show Driver -> Click shows full details and location
    drivers = User.getDrivers()

    messages = Chat.get_notifs(current_user.get_id())
    if messages:
        for message in messages:
            if message['room_id'] == str(0):
                flash("New message from drivers group chat")
            else:
                flash("New message from " + message['sender_name'])
        return redirect(url_for('drivers'))

    if request.method == 'POST':
        name = request.form.get('name')
        id = request.form.get('id')
        tracking = request.form.get('tracking')
        city = request.form.get('city')
        state = request.form.get('state')
        order_id = request.form.get('order_id')

        filtered = []

        if name:
            f = list(filter(lambda x : x['user_name'] == name, drivers))
            filtered += f

        if id:
            f = list(filter(lambda x : x['user_id'] == int(id), drivers))
            filtered += f
        
        if tracking:
            order = Package.get_driver(tracking)
            f = list(filter(lambda x : x['user_id'] == order['driver_id'], drivers))
            filtered += f

        if order_id:
            order = Package.get_order(order_id)
            f = list(filter(lambda x : x['user_id'] == order['driver_id'], drivers))
            filtered += f

        if city and not filtered:
            filtered = list(filter(lambda x : x['city'] == city, drivers))
        elif city and filtered:
            filtered = list(filter(lambda x : x['city'] == city, filtered))
        
        if state and not filtered:
            filtered = list(filter(lambda x : x['state'] == state, drivers))
        elif state and filtered:
            filtered = list(filter(lambda x : x['state'] == state, filtered))

        # If no filter, return the results from search    
        if not filtered:
            if name or id or tracking or city or state:
                filtered = []
            
            else:
                filtered = drivers

        drivers = filtered

    return render_template('drivers.html', drivers = drivers)

@app.route('/driver/<id>', methods=['GET', 'POST'])
@login_required
def driver(id):
    # Show list of orders and their statuses, current location, ID
    driver = User.get(id)
    location = User.getAddr(id)
    
    if not driver:
        return redirect(url_for(drivers))

    messages = Chat.get_notifs(current_user.get_id())
    if messages:
        for message in messages:
            if message['room_id'] == str(0):
                flash("New message from drivers group chat")
            else:
                flash("New message from " + message['sender_name'])
        return redirect(url_for('driver', id=id))

    if location:
        # For getting latitude and longitude of city and state
        geolocator = Nominatim(user_agent='my_user_agent')

        city = location['city']
        state = location['state']

        loc = geolocator.geocode(city + ', ' + state + ', ' + 'US', timeout=10000)

        # Creates map
        map = Map(
            identifier="view-side",
            lat=loc.latitude,
            lng=loc.longitude,
            zoom=11
        )

        orders = Package.get_driver_orders(id)

    else:
        map = Map(
            identifier="view-side",
            lat=0,
            lng=0,
            zoom=5
        )

    return render_template('driver.html', map=map, orders=orders, driver=driver)

@app.route('/customer_orders', methods=['GET', 'POST'])
@login_required
def customer_orders():
    # List of all orders
    # Can sort from completed and not completed
    user_id = current_user.get_id()
    
    messages = Chat.get_notifs(user_id)
    if messages:
        for message in messages:
            if message['room_id'] == str(0):
                flash("New message from drivers group chat")
            else:
                flash("New message from " + message['sender_name'])
        return redirect(url_for('orders'))

    orders = Package.get_orders()
    print(orders)
    print(user_id)
    orders = list(filter(lambda x : int(x['user_id']) == int(user_id), orders))

    return render_template('customer_orders.html', orders=orders)

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    # List of all orders
    # Can sort from completed and not completed
    if current_user.is_authenticated:
        user_id = current_user.get_id()
    
        messages = Chat.get_notifs(user_id)
        if messages:
            for message in messages:
                if message['room_id'] == str(0):
                    flash("New message from drivers group chat")
                else:
                    flash("New message from " + message['sender_name'])
            return redirect(url_for('orders'))

    orders = Package.get_orders()

    if request.method == 'POST':
        status = status = request.args.get('t', '')

        if status == 'incomplete':
            orders = list(filter(get_incompleted, orders))

        if status == 'complete':
            orders = list(filter(get_completed, orders))

    return render_template('orders.html', orders=orders)

@app.route('/driver_orders', methods=['GET', 'POST'])
def driver_orders():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))

    user_id = current_user.get_id()
    
    messages = Chat.get_notifs(user_id)
    if messages:
        for message in messages:
            if message['room_id'] == str(0):
                flash("New message from drivers group chat")
            else:
                flash("New message from " + message['sender_name'])
        return redirect(url_for('driver_orders'))
    
    orders = Package.get_driver_orders(user_id)
    status = request.args.get('t', '')

    if status == 'Incomplete':
        orders = list(filter(get_incompleted, orders))
        status = 'Completed'

    elif status == 'Completed':
        orders = list(filter(get_completed, orders))
        status = 'Incomplete'

    return render_template('driver_orders.html', orders=orders, type=status)

@app.route('/location', methods=['GET', 'POST'])
def location():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))

    user_id = current_user.get_id()

    messages = Chat.get_notifs(user_id)
    if messages:
        for message in messages:
            if message['room_id'] == str(0):
                flash("New message from drivers group chat")
            else:
                flash("New message from " + message['sender_name'])
        return redirect(url_for('location'))

    orders = Package.get_driver_orders(user_id)
    orders = list(filter(get_incompleted, orders))

    return render_template('location.html', orders=orders)

@app.route('/update_location/<id>', methods=['GET', 'POST'])
def update_location(id):
    if not current_user.is_authenticated:
        return redirect(url_for('home'))

    user_id = current_user.get_id()

    messages = Chat.get_notifs(user_id)
    if messages:
        for message in messages:
            if message['room_id'] == str(0):
                flash("New message from drivers group chat")
            else:
                flash("New message from " + message['sender_name'])
        return redirect(url_for('update_location', id=id))

    order = Package.get_order(id)
    tracking = order['tracking_id']

    messages = Chat.get_notifs(user_id)
    if messages:
        for message in messages:
            if message['room_id'] == str(0):
                flash("New message from drivers group chat")
            else:
                flash("New message from " + message['sender_name'])
        return redirect(url_for('update_location'))

    if request.method == 'POST':
        city = request.form.get('city')
        state = request.form.get('state')

        if city and state:
            addr = {
            'street1' : city,
            'street2' : city,
            'city' : city,
            'state' : state,
            'zip' : state 
            }

            user_email = Package.set_location(tracking, addr)
            User.saveAddr(user_id, city, city, state, state)

            return redirect(url_for('location'))

    return render_template('update_location.html', order=order)

@app.route('/location/complete/<id>', methods=['GET', 'POST'])
def complete(id):
    if not current_user.is_authenticated:
        return redirect(url_for('home'))

    order = Package.get_order(id)
    tracking = order['tracking_id']

    Package.set_status(tracking, 'Complete')

    addr = {
        'street1' : order['to_line1'],
        'street2' : order['to_line2'],
        'city' : order['to_city'],
        'state' : order['to_state'],
        'zip' : order['to_zip'] 
    }

    user_email = Package.set_location(tracking, addr)
    return redirect(url_for('location'))

@app.route('/review', methods=['GET', 'POST'])
def review():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))

    user_id = current_user.get_id()
    orders = Package.get_orders()
    orders = list(filter(get_completed, orders))
    orders = list(filter(lambda x : x['user_id'] == int(user_id), orders))

    id = request.args.get('id', '')

    if id:
        return redirect(url_for('submit', id=id))

    return render_template('review.html', orders = orders)

@app.route('/review/submit/<id>', methods=['GET', 'POST'])
def submit(id):
    order = Package.get_order(id)

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        if rating and comment:
            Review.create(id, order['service_type'], rating, comment)
            return redirect(url_for('review'))
    
    return render_template('review_order.html', order=order)

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    id = current_user.get_id()
    user = User.get(id)

    messages = Chat.get_notifs(id)
    if messages:
        for message in messages:
            if message['room_id'] == str(0):
                flash("New message from drivers group chat")
            else:
                flash("New message from " + message['sender_name'])
        return redirect(url_for('chat'))
    
    # Get list of all they can talk to and display
    customers = User.getCustomers()
    customers_id = get_ids(customers)
    admins = User.getAdmins()
    admins_id = get_ids(admins)
    drivers = User.getDrivers()
    drivers_id = get_ids(drivers)

    rooms = []

    id = int(id)

    if id in customers_id:
        orders = Package.get_orders()
        orders = list(filter(get_incompleted, orders))
        driverids = []

        for order in orders:
            if order['user_id'] == id:
                if order['driver_id'] not in driverids:
                    driverids.append(order['driver_id'])

        for driver in drivers:
            if driver['user_id'] in driverids:
                rooms.append(driver)

        for admin in admins:
            rooms.append(admin)

    elif id in drivers_id:
        rooms.append({
            'user_name' : 'All Drivers',
            'user_id' : '0'}) # Room for all drivers and admin
        orders = Package.get_orders()
        orders = list(filter(get_incompleted, orders))
        customerids = []

        for admin in admins:
            rooms.append(admin)

        for order in orders:
            if order['driver_id'] == id:
                if order['user_id'] not in rooms:
                    customerids.append(order['user_id'])

        for customer in customers:
            if customer['user_id'] in customerids:
                rooms.append(customer)

    elif id in admins_id:
        recv_id = drivers_id
        for admin in admins:
            recv_id.append(admin['user_id'])

        rooms.append({
            'user_name' : 'All Drivers',
            'user_id' : recv_id}) # Room for all drivers and admin

        for driver in drivers:
            rooms.append(driver)

        for customer in customers:
            rooms.append(customer)

    return render_template('chat.html', rooms=rooms, id=id, name=user.name)

@app.route('/chat/enter/<id>/<rec_id>/<name>/<rec_name>', methods=['GET', 'POST'])
def enter(id, rec_id, name, rec_name):
    session['id'] = id
    session['rec_id'] = rec_id
    session['name'] = name
    session['rec_name'] = rec_name

    return redirect(url_for('room'))

@app.route('/chat/room', methods=['GET', 'POST'])
def room():
    id = session.get('id', '')
    room_id = session.get('room_id', '')
    
    messages = Chat.get_notifs(id)
    if messages:
        for message in messages:
            if room_id != message['room_id']:
                if message['room_id'] == str(0):
                    flash("New message from drivers group chat")
                else:
                    flash("New message from " + message['sender_name'])
        return redirect(url_for('room'))

    return render_template('room.html')

@socketio.event
def join():
    id = session.get('id', '')
    rec_id = session.get('rec_id', '')
    room = ""

    if ',' in rec_id:
        room = '0'
    elif int(id) < int(rec_id):
        room = id + "," + rec_id
    else: room = rec_id + "," + id
    session['room'] = room

    join_room(room)
    rec_name = session.get('rec_name', '')

    history = Chat.get_room_history(room)

    for message in history:
        emit('my_response',
         {'date_time': message['date_time'],
            'data': message['message'],
            'name': message['user_name']})

    name = session.get('name', '')
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y %H:%M:%S")
    emit('my_response', {'date_time': date_time, 'data': name + ' is online!', 'name': 'Server'},
         to=room)

# Code from https://github.com/miguelgrinberg/Flask-SocketIO/tree/main/example
@socketio.event
def my_room_event(message):
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y %H:%M:%S")

    room = session.get('room', '')
    name = session.get('name', '')
    recv_id = session.get('rec_id', '')
    Chat.add(name, room, message['data'], date_time)
    if room == '0':
        recv_id = recv_id.strip('][').split(', ')
        for id in recv_id:
            Chat.add_notifs(name, session['id'], id, session['room'])
    else:
        Chat.add_notifs(name, session['id'], session['rec_id'], session['room'])

    emit('my_response',
         {'data': message['data'], 'date_time': date_time, 'name': name},
         to=room)

@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    name = session.get('name', '')
    room = session.get('room', '')

    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y %H:%M:%S")
   
    emit('my_response',
         {'date_time': date_time, 'data': name + ' is offline', 'name': 'Server'},
         callback=can_disconnect, to=room)

@app.route('/view_reviews', methods=['GET', 'POST'])
def view_reviews():
    reviews = Review.get_reviews()

    return render_template('view_reviews.html', reviews=reviews)

# Log out, must be logged in
@app.route('/logout')
@login_required
def logout():
    logout_user() 
    return redirect(url_for('home')) 

# For user log in
def toUserID(user_type):
    # 1:Admin, 2:Driver, 3:Customer
    if user_type == 'admin':
        return 1
    if user_type == 'driver':
        return 2
    if user_type == 'customer':
        return 3

def get_ids(users):
    ids = []

    for user in users:
        ids.append(user['user_id'])

    return ids

    
def get_unassigned(order):
    if order['order_status'] == 'Order Placed':
        return True

    else: return False

def get_completed(order):
    if order['order_status'] == "Complete":
        return True

    else: return False

def get_incompleted(order):
    if order['order_status'] != "Complete":
        return True

    else: return False

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def get_notifs(id):
    return Chat.get_notifs(id)

if __name__ == "__main__":
    socketio.run(app, debug=True, ssl_context="adhoc")
