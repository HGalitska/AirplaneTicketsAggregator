from app import app, psqldb, search_handler, arangodb, airlines_data_collection, list_of_airlines, mail
from flask import render_template, request, url_for, redirect, flash
from flask_mail import Message
from app.forms import LoginForm, RegistrationForm, SearchForm
import datetime
from app.models import Users, Flight
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import subprocess
import json

from app.search_req import SearchRequest
import os

import threading
import time
from app.mail_sender import MailSender


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('search'))


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usr = Users.query.filter_by(username=form.username).first()
        print(usr)
        if usr is None or not usr.check_password(form.password):
            flash("Error occured. Please try again.")
            return redirect(url_for('login'))
        login_user(usr)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('search')

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():

        usr = Users(username=form.username, password=form.password, first_name=form.first_name,
                    last_name=form.last_name, email=form.email)
        try:
            psqldb.session.add(usr)
        except:
            flash("Unable to add user to db")

        try:
            psqldb.session.commit()

            msg_subj = "Hello, " + str(form.first_name) + "!"
            msg = Message(msg_subj, recipients=[form.email])
            msg.html = "<p>welcome to whatafly!</p>" \
                       "<p>we hope you'll find the best deal with our help</p>" \
                       "<img src='https://www.askideas.com/media/06/Dude-I-Am-So-High-Right-Now-Funny-Plane-Meme.jpg'>"

            mail.send(msg)
        except Exception as e:
            # flash("Duplicate username or email!")
            flash("Some error accured")
            print(e)
            return redirect(url_for('signup'))
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/airlines')
def airlinesinfo():
    return render_template('airlines.html')


@app.route('/search', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    print('search')

    airports = [
        {
            "country": "Germany",
            "city": "Frankfurt",
            "airport": "FRA"
        },
        {
            "country": "Switzerland",
            "city": "Zurich",
            "airport": "ZRH"
        },
        {
            "country": "France",
            "city": "Paris",
            "airport": "DDG"
        },
        {
            "country": "Sweden",
            "city": "Stockholm",
            "airport": "NYO"
        },
        {
            "country": "Ireland",
            "city": "Dublin",
            "airport": "DUB"
        },
        {
            "country": "Norway",
            "city": "Oslo",
            "airport": "OSL"
        }, {
            "country": "Ukraine",
            "city": "Kyiv",
            "airport": "KBP"
        }, {
            "country": "Austria",
            "city": "Vienna",
            "airport": "VIE"
        }, {
            "country": "Germany",
            "city": "Berlin (Schonefeld)",
            "airport": "SXF"
        },
        {
            "country": "Cyprus",
            "city": "Larnaca",
            "airport": "LCA"
        },
        {
            "country": "Ukraine",
            "city": "Kyiv",
            "airport": "IEV"
        }
    ]
    form.departure.choices = [(airport['airport'], airport['city'] + ", " + airport['airport']) for airport in airports]
    form.arrival.choices = [(airport['airport'], airport['city'] + ", " + airport['airport']) for airport in airports]

    return render_template('search.html', airports=airports, form=form)


@app.route('/results', methods=['POST', 'GET'])
def results():
    form = request.form

    results = search_handler.handle_form(form)

    if request.method == 'POST': ''
    return render_template('results.html', results=results)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/save', methods=['POST'])
def save():
    print(request.form)
    return "ok"


@app.route('/profile/saved', methods=['POST'])
@login_required
def saved():
    user_activity = arangodb.collection('user_activity')

    user_id = current_user.get_id()
    print(user_id)
    user_data = user_activity.get(str(user_id))
    print(user_data)
    flights = []

    for flight_id in user_data['saved_flights']:
        flight = Flight.query.get(flight_id)
        flights.append(flight)

    # flights = [
    #     {
    #         "airportA": "KBP",
    #         "airportB": "FRA",s
    #         "airline": "Ryan Air",
    #         "date": datetime.datetime(2018, 9, 1, 20, 34),
    #         "duration": "3:00",
    #         "price": "43"
    #     }
    # ]

    return render_template('saved.html', saved_flights=flights)


@app.route('/profile/history', methods=['POST'])
@login_required
def history():
    routes = [
        {
            "cityA": "Kyiv",
            "cityB": "Frankfurt",
            "date": datetime.date(2018, 9, 1)
            #     this object should contain all configuration parameters to start new search
        }
    ]
    return render_template('history.html', routes=routes)


@app.route('/arango')
def arango_test():
    if arangodb.has_collection('user_activity'):
        user_activity = arangodb.collection('user_activity')
    else:
        user_activity = arangodb.create_collection('user_activity')

    # Add a hash index to the collection.
    user_activity.add_hash_index(fields=['name'], unique=False)
    # Truncate the collection.
    user_activity.truncate()

    # Insert new documents into the collection.
    user_activity.insert({'name': 'jane', 'age': 19})
    user_activity.insert({'name': 'josh', 'age': 18})
    user_activity.insert({'name': 'jake', 'age': 21})

    # Execute an AQL query. This returns a result cursor.
    cursor = arangodb.aql.execute('FOR doc IN user_activity RETURN doc')

    # Iterate through the cursor to retrieve the documents.
    student_names = [document['name'] for document in cursor]

    return len(student_names)


@app.route('/news/<airline>')
def news_airline(airline):
    # get airlines from DB and check if there is such airline
    # if airline in airlines

    if airline not in list_of_airlines:
        # TODO: show error page
        # pass
        return redirect(url_for('airlinesinfo'))
    else:

        airline_data = airlines_data_collection.get(airline)

        airline_news_data = airline_data['news']

        news = airline_news_data['v.' + str(airline_news_data['latest_version'])]

        print('news:')
        print(news)

        filename = 'json/' + airline + '_news.json'

        with open(filename) as data_file:
            json_data = data_file.read()

        arr = json.loads(json_data)

        print('arr:')
        print(arr)

        return render_template("news.html", news=arr, airline=airline)


@app.route('/updateairlinesnews')
def update_airlines_news():
    # for airline in airlines:
    #     filename = 'json/' + airline + '_news.json'
    #
    #     if os.path.exists(filename):
    #         os.remove(filename)

    subprocess.check_output(['scrapy', 'crawl', 'airlines_news_spider'])

    return redirect(url_for('airlinesinfo'))


@app.route('/updateairlinesinfo')
def update_airlines_info():
    subprocess.check_output(['scrapy', 'crawl', 'airlines_info_spider'])
    return redirect(url_for('airlinesinfo'))


# ---------------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# @app.route('/arango')
# def index():
#     arangodb.db.collection('user_activity').insert_many([
#         {'_key': 'Abby', 'age': 22},
#         {'_key': 'John', 'age': 18},
#         {'_key': 'Mary', 'age': 21}
#     ])
#
#     # Execute the query
#     cursor = arangodb.aql.execute(
#         'FOR s IN students FILTER s.age < @value RETURN s',
#         bind_vars={'value': 19}
#     )
#
#     # Iterate through the result cursor
#     # [student['_key'] for student in cursor]
#     return render_template('search.html')


# @app.route('/init_sql')
# def trypsql():
#     psqldb.create_all()
#     psqldb.session.commit()
#
#     user1 = Users('user1', 'password', 'user1@example.com', 'user1FName', 'user1LName')
#     user2 = Users('user2', 'password', 'user2@example.com', 'user2FName', 'user2LName')
#     psqldb.session.add(user1)
#     psqldb.session.add(user2)
#     psqldb.session.commit()
#     users = psqldb.session.query(Users).all()
#     return render_template('list_of_users.html', users=users)


# @app.route('/test_arangodb')
# def test_arangodb():
#     # python-arango
#     routes_stats = arangodb.collection('routes_stats')
#
#     # routes_stats.add_hash_index(fields=['route_id'], unique=True)
#     routes_stats.insert({'route_id': '2', 'data': "25:08:2018"})


# pyArango
#
# from pyArango.connection import *
#
#
# routes_stats = arangodb["routes_stats"]
#
# #  cannot find good docs, ide does not see methods of objects while working with pyArango


# ArangoPy
#
# required additional packages and some problems occurs

#
#
#
# return redirect(url_for('login'))


# @app.route('/test_update_arango')
# def test_update_arango():
#     ryanair_news = airlines_data_collection.get('ryanair')
#     updated_version = int(ryanair_news.get('updated_version'))
#     print(updated_version)
#
#     updated_version += 1
#
#     print(ryanair_news)
#
#     ryanair_news['updated_version'] = str(updated_version)
#
#     airlines_data_collection.update(ryanair_news)
#
#     return redirect(url_for('search'))


class FlightsUpdater(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)

        self.name = name
        self.isWorking = True

    def run(self):
        # time.sleep(30)
        print('Flights Updater started')
        while self.isWorking:
            saved_flights = arangodb.collection('saved_flights')
            flights = []
            print(saved_flights)

            for saved_flight in saved_flights:
                flight = Flight.query.get(saved_flight["flight_id"])
                flights.append(flight)

            for flight in flights:

                with app.test_request_context():
                    search_data = SearchRequest(flight.departure, flight.arrival, str(flight.departureTime.date()),
                                                1, 0, 0, 0, 0, False, False, False)

                    if flight.airline == 'ryanair':
                        search_data.ryanair = True
                    else:
                        if flight.airline == 'wizzair':
                            search_data.wizzair = True
                        if flight.airline == 'uia':
                            search_data.uia = True

                    # print("r: " + search_data.get('ryanair'))
                    search_results = search_handler.handle(search_data)
                    if len(search_results) > 0:
                        result = search_results[0]
                        result.get("fares")[0].get("amount")

                        print(flight.price)
                        if result.get("fares")[0].get("amount") != flight.price:
                            print("Update Found!")
                            old_price = flight.price
                            flight.price = result.get("fares")[0].get("amount")
                            psqldb.session.commit()

                            mail_sender = MailSender()
                            mail_sender.send_update(flight_id=flight.id, old_price=old_price)

            time.sleep(60 * 60)

    def stop(self):
        self.isWorking = False
