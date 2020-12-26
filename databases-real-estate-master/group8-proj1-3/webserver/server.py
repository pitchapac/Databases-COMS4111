
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
import datetime
import urllib.parse

from flask import Flask, Response, g, redirect, render_template, request, url_for, session
from sqlalchemy import *
from sqlalchemy import exc
from sqlalchemy.pool import NullPool

# accessible as a variable in index.html:

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@35.243.220.243/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.243.220.243/proj1part2"
#
DATABASEURI = "postgresql://cba2126:3534@35.231.103.173/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
# #
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute(
#     """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/', methods=['GET','POST'])
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)

    #
    # example of a database query
    #
    # cursor = g.conn.execute("SELECT name FROM test")
    # names = []
    # for result in cursor:
    #     names.append(result['name'])  # can also be accessed using result[0]
    # cursor.close()

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
   # context = dict(data=names)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    #return render_template("index.html", **context)
    return render_template("index.html")

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
    return render_template("another.html")


# # Example of adding new data to the database
# @app.route('/add', methods=['GET','POST'])
# def add():
#     name = request.form['name']
#     g.conn.execute('INSERT INTO test(name) VALUES (%s);', name)
#     g.conn.close()
#     return redirect('/')

@app.route('/login', methods=['GET','POST'])
def login():
    username = request.form['username']

    cursor = g.conn.execute(
        "SELECT person_id FROM person WHERE person_id=%s;", (username,))
    if len(cursor.fetchall()) == 0:
        # The person was not found in the database
        cursor.close()
        return render_template("invalid-login.html")
    cursor.close()
    return redirect(url_for('home', person_id=username))


@app.route('/setup-profile')
def setup_profile():
    return render_template("setup-profile.html", person_id=request.args.get('person_id'), edit=request.args.get('edit'))

@app.route('/setup-customer')
def setup_customer():
    return render_template("setup-customer.html", person_id=request.args.get('person_id'), edit=request.args.get('edit'))

@app.route('/setup-agent')
def setup_agent():
    return render_template("setup-agent.html", person_id=request.args.get('person_id'), edit=request.args.get('edit'))

@app.route('/listings')
def listings():
    return render_template("listings.html", person_id=request.args.get('person_id'), listings=request.args.get('listings'), person_type=request.args.get('person_type'))

@app.route('/reviews')
def reviews():
    # get all the agents
    cursor = g.conn.execute(
        "SELECT agent_id, name, email FROM person, agent WHERE agent_id = person_id;"
    )

    agent_list = [] 
    for result in cursor:
        one_agent = []
        one_agent.append(int(result['agent_id']))
        one_agent.append(result['name'])
        one_agent.append(result['email'])
        
        agent_list.append(one_agent)

    session['agents'] = agent_list

    # get all the customers
    cursor = g.conn.execute(
        "SELECT customer_id, name, email FROM person, customer WHERE customer_id = person_id;"
    )

    customer_list = [] 
    for result in cursor:
        one_customer = []
        one_customer.append(int(result['customer_id']))
        one_customer.append(result['name'])
        one_customer.append(result['email'])
        customer_list.append(one_customer)

    session['customers'] = customer_list
    return render_template("reviews.html", person_id=request.args.get('person_id'), agents=agent_list, customers=customer_list, reviews=request.args.get('reviews'))


@app.route('/list-selling')
def list_selling():
    return render_template("listed-properties.html", person_id=request.args.get('person_id'), edit=request.args.get('edit'))

@app.route('/represent-sold')
def represent_sold():
    return render_template("agent-sold.html", person_id=request.args.get('person_id'), edit=request.args.get('edit'))

@app.route('/represent-available')
def represent_available():
    return render_template("agent-available.html", person_id=request.args.get('person_id'), edit=request.args.get('edit'))

@app.route('/mark-property-sold')
def mark_property_sold():
    return render_template("property-sold.html", person_id=request.args.get('person_id'), property_id=request.args.get('property_id'), list_date=request.args.get('list_date'), address=request.args.get('address'), price=request.args.get('price'))

@app.route('/list-property')
def list_property():
    cursor = g.conn.execute(
        "SELECT agent_id, name FROM person, agent WHERE agent_id = person_id;"
    )

    agent_list = [] 
    for result in cursor:
        one_agent = []
        one_agent.append(int(result['agent_id']))
        one_agent.append(result['name'])
        
        agent_list.append(one_agent)

    session['agents'] = agent_list
    return render_template("list-property.html", person_id=request.args.get('person_id'), property_id=request.args.get('property_id'), propertyType=request.args.get('propertyType'), numBeds=request.args.get('numBeds'), numBaths=request.args.get('numBaths'), price=request.args.get('price'), address=request.args.get('address'), zipcode=request.args.get('zipcode'), agents=agent_list)

@app.route('/listed-sold')
def listed_sold():
    return render_template("listed-sold.html", person_id=request.args.get('person_id'))

@app.route('/review-agent')
def review_agent():
    agent_id = request.args.get('agent_id')
    cursor = g.conn.execute(
        "SELECT name, email, phone, realtor_license FROM agent, person WHERE agent.agent_id = person.person_id AND agent.agent_id=%s;",
        (agent_id,)
    )
    result = cursor.fetchone() # there will only be one row b/c query with primary key
    cursor.close()
    return render_template("review-agent.html", person_id=request.args.get('person_id'), agent_id=agent_id, name=result['name'], email=result['email'], phone=result['phone'], realtor_license=str(result['realtor_license']))

@app.route('/review-customer')
def review_customer():
    customer_id = request.args.get('customer_id')
    cursor = g.conn.execute(
        "SELECT name, email, phone FROM customer, person WHERE customer.customer_id = person.person_id AND customer.customer_id=%s;",
        (customer_id,)
    )
    result = cursor.fetchone() # there will only be one row b/c query with primary key
    cursor.close()
    return render_template("review-customer.html", person_id=request.args.get('person_id'), customer_id=customer_id, name=result['name'], email=result['email'], phone=result['phone'])


@app.route('/contact-agent', methods=['GET','POST'])
def contact_agent():
    property_id=request.args.get('property_id')
    # person_id = request.form['person_id']
    # name = request.form['name']
    # birthday = request.form['birthday']
    # email = request.form['email']
    # phone = request.form['phone']

    # cursor = g.conn.execute("SELECT MAX(person_id) AS max_id FROM person")
    # if cursor:
    #     current_max_id = cursor.first()["max_id"]
    #     new_person_id = current_max_id + 1
    # else:
    #     return render_template("error-page.html") # TODO
    cursor = g.conn.execute(
        "SELECT agent_id FROM represents WHERE property_id=%s;", (property_id,)
    )
    result_agent_id = cursor.fetchone() # only one b/c property ids are unique in this table
    agent_id = result_agent_id['agent_id']

    cursor = g.conn.execute(
        "SELECT address FROM property WHERE property_id=%s;", (property_id,)
    )
    result_address = cursor.fetchone() # only one b/c property ids are unique in this table
    address = result_address['address']

    cursor = g.conn.execute(
        "SELECT realtor_license FROM agent WHERE agent_id=%s;", (agent_id,)
    )
    result_realtor_license = cursor.fetchone()
    realtor_license = result_realtor_license['realtor_license']

    cursor = g.conn.execute(
        "SELECT name, email, phone FROM person WHERE person_id=%s;", (agent_id,)
    )
    result = cursor.fetchone()
    name = result['name']
    email = result['email']
    phone = result['phone']

    cursor.close()
    return render_template("contact-agent.html", person_id=request.args.get('person_id'), person_type=request.args.get('person_type'), agent_id=agent_id, address=address, name=name, email=email, phone=phone, realtor_license=realtor_license)

    #return redirect(url_for('home', person_id=person_id))

@app.route('/property-sold', methods=['GET','POST'])
def property_sold():
    person_id_agent = request.form['person_id']
    property_id = request.form['property_id']
    salePrice = request.form['salePrice']
    saleDate = request.form['saleDate']

    cursor = g.conn.execute(
        "INSERT INTO sold(agent_id, property_id, sale_price, sold_date) VALUES (%s, %s, %s, %s);",
        (person_id_agent, property_id, salePrice, saleDate)
    )

    cursor.close()
    return redirect(url_for('home', person_id=person_id_agent))


@app.route('/book-agent', methods=['GET','POST'])
def book_agent():
    person_id_customer = request.form['person_id']
    person_id_agent = request.form['agent_id']
    bookingDate = request.form['bookingDate']
    bookingTime = request.form['bookingTime']
    bookingLocation = request.form['bookingLocation']
    #name=name, email=email, phone=phone, realtor_license=realtor_license

    # TODO for now saying it is okay for an agent to have multiple bookings at the same time with different people cause it is annoying to handle all the webpages otherwise
    cursor = g.conn.execute(
        "SELECT appointment_date, appointment_time FROM booking, books WHERE booking.booking_id = books.booking_id AND agent_id = %s AND appointment_date = %s AND appointment_time = %s;", 
        (person_id_agent, bookingDate, bookingTime)
    )
    if len(cursor.fetchall()) != 0:
        # there is another booking for the same day and time
        return render_template("invalid-booking.html", person_id=person_id_customer)
    
    cursor = g.conn.execute("SELECT MAX(booking_id) AS max_id FROM booking;")
    if cursor:
        current_max_id = cursor.first()["max_id"]
        new_booking_id = current_max_id + 1
    # else:
    #     return render_template("error-page.html") # TODO
    cursor = g.conn.execute(
        "INSERT INTO booking(booking_id, appointment_date, appointment_time, appointment_location) VALUES (%s, %s, %s, %s);", 
        (new_booking_id, bookingDate, bookingTime, bookingLocation)
    )

    cursor = g.conn.execute(
        "INSERT INTO books(booking_id, agent_id, customer_id) VALUES (%s, %s, %s);", 
        (new_booking_id, person_id_agent, person_id_customer)
    )

    return redirect(url_for('home', person_id=person_id_customer))


@app.route('/add-profile', methods=['GET','POST'])
def add_profile():
    name = request.form['name']
    birthday = request.form['birthday']
    email = request.form['email']
    phone = request.form['phone']

    cursor = g.conn.execute("SELECT MAX(person_id) AS max_id FROM person;")
    if cursor:
        current_max_id = cursor.first()["max_id"]
        new_person_id = current_max_id + 1
    # else:
    #     return render_template("error-page.html") # TODO
    cursor = g.conn.execute(
        "INSERT INTO Person(Person_ID, Name, Date_Of_Birth, Email, Phone) VALUES (%s, %s, %s, %s, %s);", 
        (new_person_id, name, birthday, email, phone)
    )
    
    cursor.close()
    return redirect(url_for('home', person_id=new_person_id))

@app.route('/add-customer', methods=['GET','POST'])
def add_customer():
    #person_id=request.args.get('person') # get the person id from the url
    person_id = request.form['person_id']
    propertyType = request.form['propertyType']
    maxBudget = request.form['maxBudget']
    minBudget = request.form['minBudget']
    desiredBeds = request.form['desiredBeds']
    desiredBaths = request.form['desiredBaths']
    zipcode = request.form['zipcode']

    cursor = g.conn.execute(
        "INSERT INTO customer(customer_id, max_budget, min_budget, desired_beds, desired_baths, desired_zipcode, desired_property_type) VALUES (%s, %s, %s, %s, %s, %s, %s);", 
        (person_id, maxBudget, minBudget, desiredBeds, desiredBaths, zipcode, propertyType)
    )
  
    cursor.close()
    return redirect(url_for('home', person_id=person_id))

@app.route('/add-agent', methods=['GET','POST'])
def add_agent():
    #person_id=request.args.get('person') # get the person id from the url
    person_id = request.form['person_id']
    realtorLicense = request.form['realtorLicense']

    # TODO will there ever be database errors for invalid input? test manually and see if can make happen

   # try:
    cursor = g.conn.execute(
        "INSERT INTO agent(agent_id, realtor_license) VALUES (%s, %s);", 
        (person_id, realtorLicense)
    )

    cursor.close()
    return redirect(url_for('home', person_id=person_id))

@app.route('/show-customer-bookings', methods=['GET','POST'])
def show_customer_bookings():
    #person_id = request.form['person_id']
    person_id=request.args.get('person_id')
    todays_date = datetime.datetime.now().date()

    cursor = g.conn.execute(
        "SELECT agent.agent_id, person.name, person.email, person.phone, agent.realtor_license, appointment_date, appointment_time, appointment_location FROM books, booking, person, agent WHERE books.booking_id = booking.booking_id AND person.person_id = books.agent_id AND books.agent_id = agent.agent_id AND books.customer_id = %s AND appointment_date < %s;", 
        (person_id, todays_date)
    )

    prior_bookings = []
    headers = ['Agent Name', 'Appointment Date', 'Appointment Time', 'Appointment Location', 'Review Agent']
    prior_bookings.append(headers)
    for result in cursor:
        booking = []
        booking.append(result['name'])
        booking.append(result['appointment_date'])
        booking.append(result['appointment_time'])
        booking.append(result['appointment_location'])
        agent_review= "<a href=\"/review-agent?person_id="+str(person_id)+ "&agent_id="+ str(result['agent_id']) +"\">Review Agent</a>"
        
        booking.append(agent_review)
        prior_bookings.append(booking)

    # find the upcoming bookings (including today)
    cursor = g.conn.execute(
        "SELECT person.name, appointment_date, appointment_time, appointment_location FROM books, booking, person WHERE books.booking_id = booking.booking_id AND person.person_id = books.agent_id AND books.customer_id = %s AND appointment_date >= %s;", 
        (person_id, todays_date)
    )

    upcoming_bookings = [] 
    headers = ['Agent Name', 'Appointment Date', 'Appointment Time', 'Appointment Location']
    upcoming_bookings.append(headers)
    for result in cursor:
        booking = []
        booking.append(result['name'])
        booking.append(result['appointment_date'])
        booking.append(result['appointment_time'])
        booking.append(result['appointment_location'])
        print("LOCATION " + str(result['appointment_location']))
        upcoming_bookings.append(booking)

    cursor.close()

    session['prior-bookings'] = prior_bookings
    session['upcoming-bookings'] = upcoming_bookings

    return render_template("customer-bookings.html", person_id=request.args.get('person_id'))

@app.route('/show-agent-bookings', methods=['GET','POST'])
def show_agent_bookings():
    person_id=request.args.get('person_id')
    todays_date = datetime.datetime.now().date()

    cursor = g.conn.execute(
        "SELECT customer.customer_id, person.name, person.email, person.phone, appointment_date, appointment_time, appointment_location FROM books, booking, person, customer WHERE books.booking_id = booking.booking_id AND person.person_id = books.customer_id AND books.customer_id = customer.customer_id AND books.agent_id = %s AND appointment_date < %s;", 
        (person_id, todays_date)
    )

    prior_bookings = []
    headers = ['Customer Name', 'Appointment Date', 'Appointment Time', 'Appointment Location', 'Review Customer']
    prior_bookings.append(headers)
    for result in cursor:
        booking = []
        booking.append(result['name'])
        booking.append(result['appointment_date'])
        booking.append(result['appointment_time'])
        booking.append(result['appointment_location'])
        customer_review= "<a href=\"/review-customer?person_id="+str(person_id)+ "&customer_id="+ str(result['customer_id']) +"\">Review Customer</a>"
        
        booking.append(customer_review)
        prior_bookings.append(booking)

    # find the upcoming bookings (including today)
    cursor = g.conn.execute(
        "SELECT person.name, appointment_date, appointment_time, appointment_location FROM books, booking, person WHERE books.booking_id = booking.booking_id AND person.person_id = books.customer_id AND books.agent_id = %s AND appointment_date >= %s;", 
        (person_id, todays_date)
    )

    upcoming_bookings = []
    headers = ['Customer Name', 'Appointment Date', 'Appointment Time', 'Appointment Location']
    upcoming_bookings.append(headers)
    for result in cursor:
        booking = []
        booking.append(result['name'])
        booking.append(result['appointment_date'])
        booking.append(result['appointment_time'])
        booking.append(result['appointment_location'])
        upcoming_bookings.append(booking)

    cursor.close()

    session['prior-bookings'] = prior_bookings
    session['upcoming-bookings'] = upcoming_bookings

    return render_template("customer-bookings.html", person_id=request.args.get('person_id'))

@app.route('/new-agent-review', methods=['GET','POST'])
def new_agent_reivew():
    person_id_customer_writer = request.form['person_id']
    person_id_agent = request.form['agent_id']
    
    cursor = g.conn.execute("SELECT MAX(post_id) AS max_id FROM review_post;")
    if cursor:
        current_max_id = cursor.first()["max_id"]
        new_post_id = current_max_id + 1
    # else: # TODO error page/crash gracefully
    ratingNumber  = int(request.form['ratingNumber'])
    reviewText = request.form['reviewText']

    cursor = g.conn.execute("INSERT INTO review_post(post_id, rating_number, review_text) VALUES (%s, %s, %s);",
        (new_post_id, ratingNumber, reviewText)
    )
    cursor = g.conn.execute("INSERT INTO agent_review(post_id, agent_id, customer_id) VALUES (%s, %s, %s);",
        (new_post_id, person_id_agent, person_id_customer_writer)
    )
    
    cursor.close()

    return redirect(url_for('home', person_id=person_id_customer_writer))

@app.route('/new-customer-review', methods=['GET','POST'])
def new_customer_reivew():
    person_id_agent_writer = request.form['person_id']
    person_id_customer = request.form['customer_id']
    
    cursor = g.conn.execute("SELECT MAX(post_id) AS max_id FROM review_post;")
    if cursor:
        current_max_id = cursor.first()["max_id"]
        new_post_id = current_max_id + 1
    # else: # TODO error page/crash gracefully
    ratingNumber  = int(request.form['ratingNumber'])
    reviewText = request.form['reviewText']

    cursor = g.conn.execute("INSERT INTO review_post(post_id, rating_number, review_text) VALUES (%s, %s, %s);",
        (new_post_id, ratingNumber, reviewText)
    )
  
    cursor = g.conn.execute("INSERT INTO customer_review(post_id, customer_id, agent_id) VALUES (%s, %s, %s);",
        (new_post_id, person_id_customer, person_id_agent_writer)
    )
    
    cursor.close()


    return redirect(url_for('home', person_id=person_id_agent_writer))



@app.route('/save-property', methods=['GET','POST'])
def save_property():
    person_id = request.args.get('person_id')
    property_id = request.args.get('property_id')

    try:
        cursor = g.conn.execute(
            "INSERT INTO saves(customer_id, property_id) VALUES(%s, %s);",
            (person_id, property_id)
        )
        cursor.close()
    except exc.IntegrityError:
        pass

    return redirect(url_for('home', person_id=person_id))



@app.route('/filter-listings', methods=['GET','POST'])
def filter_listings():
    person_id = request.form['person_id']

    person_type = "None"
    cursor = g.conn.execute(
        "SELECT customer_id FROM customer WHERE customer_id=%s;", person_id)
    if len(cursor.fetchall()) != 0:
        person_type = "customer"

    
    property_type  = request.form['propertyType']
    maxBudget = request.form['maxBudget']
    minBudget = request.form['minBudget']
    desiredBeds = request.form['desiredBeds']
    desiredBaths = request.form['desiredBaths']
    desiredZipcode = request.form['zipcode']
    filters = {'maximum price':maxBudget, 'minimum price':minBudget, 'desired beds':desiredBeds, 'desired baths':desiredBaths, 'zipcode':desiredZipcode}
    session['filters'] = filters

    if property_type == "rentable":
        cursor = g.conn.execute(
            "SELECT rentable_id AS property_id, day_listed, num_beds, num_baths, address, zipcode, monthly_rent AS price FROM property, rentable WHERE property.property_id NOT IN (select property_id FROM sold) AND property.property_id = rentable.rentable_id AND rentable.monthly_rent >= %s AND rentable.monthly_rent <= %s AND property.num_beds = %s AND property.num_baths = %s AND property.zipcode LIKE %s;", 
            (minBudget, maxBudget, desiredBeds, desiredBaths, desiredZipcode)
        )
    elif property_type == "buyable":
        cursor = g.conn.execute(
            "SELECT buyable_id AS property_id, day_listed, num_beds, num_baths, address, zipcode, total_price AS price FROM property, buyable WHERE property.property_id NOT IN (select property_id FROM sold) AND property.property_id = buyable.buyable_id AND buyable.total_price >= %s AND buyable.total_price <= %s AND property.num_beds = %s AND property.num_baths = %s AND property.zipcode LIKE %s;", 
            (minBudget, maxBudget, desiredBeds, desiredBaths, desiredZipcode)
        )

    all_listings = []
    headers = ['Day Listed', 'Number of Beds', 'Number of Baths', 'Address', 'Zipcode', 'Price']
    if person_type == "customer":
        headers.append('Contact Agent')
        headers.append('Save Property')

    all_listings.append(headers)
    for result in cursor:
        listing = []
        listing.append(result['day_listed'].date())
        listing.append(int(result['num_beds']))
        listing.append(int(result['num_baths']))
        listing.append(result['address'])
        listing.append(result['zipcode'])
        listing.append(float(result['price']))

        if person_type == "customer":
            agent_contact_link= "<a href=\"/contact-agent?person_id="+str(person_id)+ "&person_type="+ str(person_type) + "&property_id="+str(result['property_id'])+"\">Contact Agent</a>"
            listing.append(agent_contact_link)
            
            save_property_link= "<a href=\"/save-property?person_id="+str(person_id)+ "&property_id="+str(result['property_id'])+"\">Save Property</a>"
            listing.append(save_property_link)
        all_listings.append(listing)

    cursor.close()

    session['listings'] =   all_listings

    return redirect(url_for('listings', person_id=person_id, person_type=person_type))


@app.route('/filter-reviews-ratings', methods=['GET','POST'])
def filter_reviews_ratings():
    person_id = request.form['person_id']

    selectedRating = request.form['selectedRating']

    # get all the review posts for reviews written about the customer in customer_review 
    cursor = g.conn.execute(
            "SELECT  rating_number, review_text, person1.name AS agent_name, person1.email AS agent_email, person2.name AS customer_name, person2.email AS customer_email FROM agent_review, review_post, person AS person1, person AS person2 WHERE agent_review.post_id = review_post.post_id AND person2.person_id = agent_review.agent_id AND person1.person_id = agent_review.customer_id AND review_post.rating_number = %s;", 
            (selectedRating,)
        )

    reviews = []
    headers = ['Reviewee Agent Name', 'Reviewee Agent Email','Reviewer Customer Name', 'Reviewer Customer Email',  'Rating Number', 'Review Text']
    reviews.append(headers)
    for result in cursor:
        review = []
        review.append(result['customer_name'])
        review.append(result['customer_email'])
        review.append(result['agent_name'])
        review.append(result['agent_email']) 
        review.append(int(result['rating_number']))
        review.append(result['review_text'])
        reviews.append(review)


    cursor.close()

    session['reviews'] =   reviews

    return redirect(url_for('reviews', person_id=person_id))



@app.route('/filter-reviews-agents', methods=['GET','POST'])
def filter_reviews_agents():
    person_id = request.form['person_id']

    selectedAgent = request.form['selectedAgent']

    # get all the review posts for reviews written about the customer in customer_review 
    cursor = g.conn.execute(
            "SELECT  rating_number, review_text, person1.name AS agent_name, person1.email AS agent_email, person2.name AS customer_name, person2.email AS customer_email FROM agent_review, review_post, person AS person1, person AS person2 WHERE agent_review.post_id = review_post.post_id AND agent_review.agent_id = %s AND person2.person_id = agent_review.agent_id AND person1.person_id = agent_review.customer_id;", 
            (selectedAgent,)
        )

    reviews = []
    headers = ['Reviewee Agent Name', 'Reviewee Agent Email','Reviewer Customer Name', 'Reviewer Customer Email',  'Rating Number', 'Review Text']
    reviews.append(headers)
    for result in cursor:
        review = []
        review.append(result['customer_name'])
        review.append(result['customer_email'])
        review.append(result['agent_name'])
        review.append(result['agent_email'])
        review.append(int(result['rating_number']))
        review.append(result['review_text'])
        reviews.append(review)


    cursor.close()

    session['reviews'] =   reviews

    return redirect(url_for('reviews', person_id=person_id))



@app.route('/filter-reviews-customers', methods=['GET','POST'])
def filter_reviews_customers():
    person_id = request.form['person_id']

    selectedCustomer = request.form['selectedCustomer']

    # get all the review posts for reviews written about the customer in customer_review 
    cursor = g.conn.execute(
            "SELECT  rating_number, review_text, person1.name AS agent_name, person1.email AS agent_email, person2.name AS customer_name, person2.email AS customer_email FROM customer_review, review_post, person AS person1, person AS person2 WHERE customer_review.post_id = review_post.post_id AND customer_review.customer_id = %s AND person2.person_id = customer_review.customer_id AND person1.person_id = customer_review.agent_id;", 
            (selectedCustomer,)
        )

    reviews = []
    headers = ['Reviewee Customer Name', 'Reviewee Customer Email', 'Reviwer Agent Name', 'Reviewer Agent Email', 'Rating Number', 'Review Text']
    reviews.append(headers)
    for result in cursor:
        review = []
        review.append(result['customer_name'])
        review.append(result['customer_email'])
        review.append(result['agent_name'])
        review.append(result['agent_email'])
        review.append(int(result['rating_number']))
        review.append(result['review_text'])
        reviews.append(review)


    cursor.close()

    session['reviews'] =   reviews

    return redirect(url_for('reviews', person_id=person_id))

@app.route('/customer-listings', methods=['GET','POST'])
def customer_listings():
    # only called for customers
    person_id=request.args.get('person_id')

    # pre-fillin listing results based on customer's settings
    cursor = g.conn.execute(
        "SELECT customer_id, max_budget, min_budget, desired_beds, desired_baths, desired_zipcode, desired_property_type FROM customer WHERE customer_id=%s;", 
        (person_id,)
    )
    
    customer_info = cursor.fetchone() # there will only ever be one row b/c query with primary key
    print("CUSTOMER INFO " + str(customer_info))
    property_type = customer_info['desired_property_type']
    if property_type == 'rentable':
        cursor = g.conn.execute(
            "SELECT rentable_id AS property_id, day_listed, num_beds, num_baths, address, zipcode, monthly_rent AS price FROM property, rentable WHERE property.property_id NOT IN (select property_id FROM sold) AND property.property_id = rentable.rentable_id AND rentable.monthly_rent >= %s AND rentable.monthly_rent <= %s AND property.num_beds = %s AND property.num_baths = %s AND property.zipcode LIKE %s;", 
            (int(customer_info['min_budget']), int(customer_info['max_budget']), customer_info['desired_beds'], customer_info['desired_baths'], customer_info['desired_zipcode'])
    )
    elif property_type == "buyable":
        cursor = g.conn.execute(
            "SELECT buyable_id AS property_id, day_listed, num_beds, num_baths, address, zipcode, total_price AS price FROM property, buyable WHERE property.property_id NOT IN (select property_id FROM sold) AND property.property_id = buyable.buyable_id AND buyable.total_price >= %s AND buyable.total_price <= %s AND property.num_beds = %s AND property.num_baths = %s AND property.zipcode LIKE %s;", 
            (int(customer_info['min_budget']), int(customer_info['max_budget']), customer_info['desired_beds'], customer_info['desired_baths'], customer_info['desired_zipcode'])
    )
        
    filters = {'maximum price':int(customer_info['max_budget']), 'minimum price':int(customer_info['min_budget']), 'desired beds':int(customer_info['desired_beds']), 'desired baths':int(customer_info['desired_baths']), 'zipcode':customer_info['desired_zipcode']}
    session['filters'] = filters

    all_listings = []
    headers = ['Day Listed', 'Number of Beds', 'Number of Baths', 'Address', 'Zipcode', 'Price', 'Contact Agent', 'Save Property']
    all_listings.append(headers)
    for result in cursor:
        listing = []
        listing.append(result['day_listed'].date())
        listing.append(int(result['num_beds']))
        listing.append(int(result['num_baths']))
        listing.append(result['address'])
        listing.append(result['zipcode'])
        listing.append(int(result['price']))

        agent_contact_link= "<a href=\"/contact-agent?person_id="+str(person_id)+ "&person_type="+ "customer" + "&property_id="+str(result['property_id'])+"\">Contact Agent</a>"
        listing.append(agent_contact_link)

        save_property_link= "<a href=\"/save-property?person_id="+str(person_id)+ "&property_id="+str(result['property_id'])+"\">Save Property</a>"
        listing.append(save_property_link)
        all_listings.append(listing)


    cursor.close()

    session['listings'] =   all_listings
    return redirect(url_for('listings', person_id=person_id, person_type="customer"))



@app.route('/new-list-property', methods=['GET','POST'])
def new_list_property():
    person_id = request.form['person_id']
    numBeds = request.form['numBeds']
    numBaths = request.form['numBaths']
    price = request.form['price']
    address = request.form['address']
    zipcode = request.form['zipcode']

    if request.form['property_id'] == 'None':
        # not an edit; new listing
        property_type  = request.form['propertyType']
        selectedAgent = request.form['selectedAgent']
        cursor = g.conn.execute("SELECT MAX(property_id) AS max_id FROM property")
        if cursor:
            current_max_id = cursor.first()["max_id"]
            new_property_id = current_max_id + 1
        # else:
        #     return render_template("error-page.html") # TODO
    
        # all the not sold properties: select day_listed, num_beds, num_baths, zipcode from property where property_id not in (select property_id from sold) and property_id in (select property_id from %s where ), property_type;
        todays_date = datetime.datetime.now().date()
        cursor = g.conn.execute(
            "INSERT INTO property(property_id, seller_id, day_listed, num_beds, num_baths, address, zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s);",
            (new_property_id, person_id, todays_date, numBeds, numBaths, address, zipcode)
        )
        if property_type == "rentable": 
            cursor = g.conn.execute(
                "INSERT INTO rentable(rentable_id, monthly_rent) VALUES (%s, %s);",
                (new_property_id, price)
            )
        elif property_type == "buyable":
            cursor = g.conn.execute(
                "INSERT INTO buyable(buyable_id, total_price) VALUES (%s, %s);",
                (new_property_id, price)
            )
        
        cursor = g.conn.execute(
            "INSERT INTO represents(agent_id, property_id) VALUES (%s, %s);",
            (selectedAgent, new_property_id)
        )
        
        
    else:
        # this is an edit -- can't change property type nor agent
        property_id = request.form['property_id']
        existing_property_type  = request.form['existingPropertyType']

        cursor = g.conn.execute(
            "UPDATE property SET num_beds = %s,  num_baths = %s, address = %s, zipcode = %s WHERE property_id = %s;", 
            (numBeds, numBaths, address, zipcode, property_id)
        )
       
        if existing_property_type == "apartment": 
            cursor = g.conn.execute(
                "UPDATE rentable SET monthly_rent = %s WHERE rentable_id = %s;",
                (price, property_id)
            )
       
        elif existing_property_type == "house":
            cursor = g.conn.execute(
                "UPDATE buyable SET total_price = %s WHERE buyable_id = %s;",
                (price, property_id)
            )

    cursor.close()
    return redirect(url_for('home', person_id=person_id))

@app.route('/listed-properties-sold', methods=['GET','POST'])
def listed_properties_sold():
    person_id=request.args.get('person_id')
    cursor = g.conn.execute("SELECT table_1.property_id,  table_1.day_listed,  table_1.num_beds,  table_1.num_baths,  table_1.address,  table_1.zipcode, (CASE WHEN table_1.property_id IN (SELECT rentable_id FROM rentable) THEN 'apartment' ELSE 'house' END) AS property_type, (CASE WHEN table_1.property_id IN (SELECT rentable_id FROM rentable) THEN (SELECT monthly_rent from rentable WHERE rentable_id = table_1.property_id) ELSE (SELECT total_price FROM buyable WHERE buyable_id = table_1.property_id) END) AS price, name AS agent_name, email AS agent_email, phone AS agent_phone FROM (SELECT property_id, day_listed, num_beds, num_baths, address, zipcode FROM property LEFT OUTER JOIN buyable ON property_id = buyable_id WHERE property.property_id IN (SELECT property_id FROM sold) AND property.seller_id = %s) AS table_1 INNER JOIN (SELECT property_id FROM property LEFT OUTER JOIN rentable ON property_id = rentable_id WHERE property.property_id IN (SELECT property_id FROM sold) AND property.seller_id = %s) AS table_2 ON table_1.property_id = table_2.property_id INNER JOIN (SELECT property_id, name, email, phone FROM represents, person WHERE person_id = agent_id) AS table_3 ON table_3.property_id = table_2.property_id;", (person_id, person_id))
    headers = ['Day Listed', 'Number of Beds', 'Number of Baths', 'Address', 'Zipcode', 'Property Type', 'Price', "Agent Name" , "Agent Email", "Agent Phone"]
    propertylist = []
    propertylist.append(headers)
    for result in cursor:
        templist = []
        templist.append(result['day_listed'])
        templist.append(int(result['num_beds']))
        templist.append(int(result['num_baths']))
        templist.append(result['address'])
        templist.append(result['zipcode'])
        templist.append((result['property_type']))
        templist.append(int(result['price']))
        templist.append((result['agent_name']))
        templist.append((result['agent_email']))
        templist.append(result['agent_phone'])
        propertylist.append(templist)         
    cursor.close()
    session['sold_prop'] = propertylist
    return redirect(url_for('listed_sold', person_id=person_id))


@app.route('/listed-properties', methods=['GET','POST'])
def listed_properties():
    person_id=request.args.get('person_id')
    cursor = g.conn.execute("SELECT table_1.property_id,  table_1.day_listed,  table_1.num_beds,  table_1.num_baths,  table_1.address,  table_1.zipcode, (CASE WHEN table_1.property_id IN (SELECT rentable_id FROM rentable) THEN 'apartment' ELSE 'house' END) AS property_type, (CASE WHEN table_1.property_id IN (SELECT rentable_id FROM rentable) THEN (SELECT monthly_rent from rentable WHERE rentable_id = table_1.property_id) ELSE (SELECT total_price FROM buyable WHERE buyable_id = table_1.property_id) END) AS price, name AS agent_name, email AS agent_email, phone AS agent_phone FROM (SELECT property_id, day_listed, num_beds, num_baths, address, zipcode FROM property LEFT OUTER JOIN buyable ON property_id = buyable_id WHERE property.property_id NOT IN (SELECT property_id FROM sold) AND property.seller_id = %s) AS table_1 INNER JOIN (SELECT property_id FROM property LEFT OUTER JOIN rentable ON property_id = rentable_id WHERE property.property_id NOT IN (SELECT property_id FROM sold) AND property.seller_id = %s) AS table_2 ON table_1.property_id = table_2.property_id INNER JOIN (SELECT property_id, name, email, phone FROM represents, person WHERE person_id = agent_id) AS table_3 ON table_3.property_id = table_2.property_id;", (person_id, person_id))
    headers = ['Day Listed', 'Number of Beds', 'Number of Baths', 'Address', 'Zipcode', 'Property Type', 'Price', 'Agent Name','Agent Email','Agent Phone','Edit Listing']
    propertylist = []
    propertylist.append(headers)
    for result in cursor:
        templist = []
        templist.append(result['day_listed'])
        templist.append(int(result['num_beds']))
        templist.append(int(result['num_baths']))
        templist.append(result['address'])
        templist.append(result['zipcode'])
        templist.append((result['property_type']))
        templist.append(int(result['price']))
        templist.append((result['agent_name']))
        templist.append((result['agent_email']))
        templist.append(result['agent_phone'])
        edit_listing = "<a href=\"/list-property?person_id="+str(person_id)+ "&property_id="+ str(result['property_id']) + "&propertyType="+ str(result['property_type']) +"&numBeds="+ str(result['num_beds'])+"&numBaths="+ str(result['num_baths'])+"&price="+ str(result['price'])+"&address="+ urllib.parse.quote(result['address'], safe='')+"&zipcode="+ str(result['zipcode'])+"\">Edit Listing</a>"
        templist.append(edit_listing)
        propertylist.append(templist)         
    cursor.close()
    session['available_prop'] = propertylist
    return redirect(url_for('list_selling', person_id=person_id))

@app.route('/agent-sold', methods=['GET','POST'])
def agent_sold():
    person_id=request.args.get('person_id')
    cursor = g.conn.execute(
        "SELECT property.property_id,  day_listed, num_beds, num_baths, address, zipcode, (CASE WHEN property.property_id IN (SELECT rentable_id FROM rentable) THEN 'apartment' ELSE 'house' END) AS property_type, (CASE WHEN property.property_id IN (SELECT rentable_id FROM rentable) THEN (SELECT monthly_rent from rentable WHERE rentable_id = property.property_id) ELSE (SELECT total_price FROM buyable WHERE buyable_id = property.property_id) END) AS price, sale_price, sold_date, person.name AS seller_name, person.phone AS seller_phone, person.email AS seller_email FROM represents, property, person, sold WHERE represents.agent_id = %s AND represents.property_id = property.property_id AND property.property_id IN (SELECT property_id FROM sold) AND person_id = property.seller_id AND property.property_id = sold.property_id",  
        (person_id,)
    )
    headers = ['Property ID', 'Day Listed','Number of Beds', 'Number of Baths', 'Address', 'Zipcode', 'Property Type', 'Price', 'Sold Price','Sold Date','Seller Name', 'Seller Phone','Seller Email']
    propertylist = []
    propertylist.append(headers)
    for result in cursor:
        templist = []
        templist.append(int(result['property_id']))
        templist.append(result['day_listed'])
        templist.append(int(result['num_beds']))
        templist.append(int(result['num_baths']))
        templist.append(result['address'])
        templist.append(result['zipcode'])
        templist.append((result['property_type']))
        templist.append(int(result['price']))
        templist.append(int(result['sale_price']))
        templist.append((result['sold_date']))
        templist.append((result['seller_name']))
        templist.append((result['seller_phone']))
        templist.append((result['seller_email']))
        propertylist.append(templist)         
    cursor.close()
    session['sold_listing'] = propertylist
    return redirect(url_for('represent_sold', person_id=person_id))

@app.route('/agent-available', methods=['GET','POST'])
def agent_available():
    person_id=request.args.get('person_id')
    cursor = g.conn.execute(
        "SELECT property.property_id,  day_listed, num_beds, num_baths, address, zipcode, (CASE WHEN property.property_id IN (SELECT rentable_id FROM rentable) THEN 'apartment' ELSE 'house' END) AS property_type, (CASE WHEN property.property_id IN (SELECT rentable_id FROM rentable) THEN (SELECT monthly_rent from rentable WHERE rentable_id = property.property_id) ELSE (SELECT total_price FROM buyable WHERE buyable_id = property.property_id) END) AS price, person.name AS seller_name, person.phone AS seller_phone, person.email AS seller_email FROM represents, property, person WHERE represents.agent_id = %s AND represents.property_id = property.property_id AND property.property_id NOT IN (SELECT property_id FROM sold) AND person_id = property.seller_id",  
        (person_id,)
    )
    headers = ['Property ID', 'Day Listed','Number of Beds', 'Number of Baths', 'Address', 'Zipcode', 'Property Type', 'Price', 'Seller Name', 'Seller Phone','Seller Email', 'Mark Sold']
    propertylist = []
    propertylist.append(headers)
    for result in cursor:
        templist = []
        templist.append(int(result['property_id']))
        templist.append(result['day_listed'])
        templist.append(int(result['num_beds']))
        templist.append(int(result['num_baths']))
        templist.append(result['address'])
        templist.append(result['zipcode'])
        templist.append((result['property_type']))
        templist.append(int(result['price']))
        templist.append((result['seller_name']))
        templist.append((result['seller_phone']))
        templist.append((result['seller_email']))
        mark_property_sold= "<a href=\"/mark-property-sold?person_id="+str(person_id)+ "&property_id="+str(result['property_id']) + "&list_date="+str(result['day_listed']) +"&address="+ urllib.parse.quote(result['address'], safe='')+ "&price="+str(result['price'])  +"\">Mark property as sold</a>"
        templist.append(mark_property_sold)
        propertylist.append(templist)         
    cursor.close()
    session['available_listing'] = propertylist
    return redirect(url_for('represent_available', person_id=person_id))




@app.route('/edit-profile', methods=['GET','POST'])
def edit_profile():
    person_id = request.form['person_id']
    name = request.form['name']
    birthday = request.form['birthday']
    email = request.form['email']
    phone = request.form['phone']

    cursor = g.conn.execute(
        "UPDATE person SET name= %s, Date_Of_Birth = %s,  Email = %s, Phone = %s WHERE person_id = %s", 
        (name, birthday, email, phone, person_id)
    )
    
    cursor.close()
    return redirect(url_for('home', person_id=person_id))

@app.route('/edit-customer', methods=['GET','POST'])
def edit_customer():
    person_id = request.form['person_id']
    propertyType = request.form['propertyType']
    maxBudget = request.form['maxBudget']
    minBudget = request.form['minBudget']
    desiredBeds = request.form['desiredBeds']
    desiredBaths = request.form['desiredBaths']
    zipcode = request.form['zipcode']

    # TODO will there ever be database errors for invalid input? test manually and see if can make happen

    cursor = g.conn.execute(
        "UPDATE customer SET max_budget = %s, min_budget = %s, desired_beds = %s, desired_baths = %s, desired_zipcode = %s, desired_property_type = %s  WHERE customer_id = %s", 
        (maxBudget, minBudget, desiredBeds, desiredBaths, zipcode, propertyType, person_id)
    )

    cursor.close()
    return redirect(url_for('home', person_id=person_id))

@app.route('/edit-agent', methods=['GET','POST'])
def edit_agent():
    person_id = request.form['person_id']
    realtorLicense = request.form['realtorLicense']

    cursor = g.conn.execute(
        "UPDATE agent SET realtor_license = %s WHERE agent_id = %s", 
        (realtorLicense, person_id)
    )

    cursor.close()
    return redirect(url_for('home', person_id=person_id))


@app.route('/delete-saved-property', methods=['GET','POST'])
def delete_saved_property():
    person_id_customer=request.args.get('person_id')
    property_id=request.args.get('property_id')

    cursor = g.conn.execute(
        "DELETE FROM saves WHERE customer_id = %s and property_id = %s",
        (person_id_customer, property_id)
    )

    return redirect(url_for('home', person_id=person_id_customer))

@app.route('/home', methods=['GET','POST'])
def home():
    person_id=request.args.get('person_id')

    is_customer = "False"
    cursor = g.conn.execute(
        "SELECT customer_id FROM customer WHERE customer_id=%s", (person_id,))
    savedproperty = []
    if len(cursor.fetchall()) != 0:
        # The person is a customer
        is_customer = "True"
        cursor = g.conn.execute(
            "SELECT saves.property_id, seller_id, day_listed, num_beds, num_baths, address, zipcode, (CASE WHEN saves.property_id IN (SELECT rentable_id FROM rentable) THEN 'apartment' ELSE 'house' END) AS property_type,(CASE WHEN saves.property_id IN (SELECT rentable_id FROM rentable) THEN (SELECT monthly_rent from rentable WHERE rentable_id = saves.property_id) ELSE (SELECT total_price FROM buyable WHERE buyable_id = saves.property_id) END) AS price FROM property, saves WHERE customer_id= %s AND saves.property_id = property.property_id;", 
            (person_id,)
        )
        for result in cursor:
            templist = []
            templist.append(result['day_listed'])
            templist.append(result['num_beds'])
            templist.append(result['num_baths'])
            templist.append(result['address'])
            templist.append(result['zipcode'])
            templist.append(result['property_type'])
            templist.append(result['price'])
            delete_saved_property= "<a href=\"/delete-saved-property?person_id="+str(person_id)+ "&property_id="+str(result['property_id'])+"\">Delete Saved Property</a>"
            templist.append(delete_saved_property)
            
            agent_contact_link= "<a href=\"/contact-agent?person_id="+str(person_id)+ "&person_type="+ "customer" + "&property_id="+str(result['property_id'])+"\">Contact Agent</a>"
            templist.append(agent_contact_link)
        
            savedproperty.append(templist)         
        cursor.close()

    is_agent = "False"
    cursor = g.conn.execute(
        "SELECT agent_id FROM agent WHERE agent_id=%s", (person_id,))
    if len(cursor.fetchall()) != 0:
        # The person is an agent
        is_agent = "True"

    cursor.close()
    return render_template("home.html", person_id=person_id,
        is_customer=is_customer, is_agent=is_agent, saved_prop=savedproperty)



if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.secret_key = 'super secret key'
        app.config['SESSION_TYPE'] = 'filesystem'

       # session.init_app(app)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
