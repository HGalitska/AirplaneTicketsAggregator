from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.types import DateTime, Integer, String
from sqlalchemy.sql import func

from app import psqldb, login


@login.user_loader
def load_user(id):
    return User.query.get(id)


class User(psqldb.Model, UserMixin):
    __tablename__ = 'Users'

    id = psqldb.Column(psqldb.Integer, unique=True, primary_key=True, nullable=False, autoincrement=True)
    username = psqldb.Column(psqldb.String(128), unique=True, nullable=False)
    password = psqldb.Column(psqldb.String(256), nullable=False)
    email = psqldb.Column(psqldb.String(128), unique=True, nullable=False)
    first_name = psqldb.Column(psqldb.String(256), nullable=False)
    last_name = psqldb.Column(psqldb.String(256), nullable=False)

    def __init__(self, username, password, email, first_name, last_name):
        self.username = username
        self.email = email  # .lower
        self.first_name = first_name
        self.last_name = last_name
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Log(psqldb.Model):
    __tablename__ = 'Logs'
    id = psqldb.Column(Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)  # auto incrementing
    created_at = psqldb.Column(DateTime, default=func.now(), nullable=False)  # the current timestamp
    pathname = psqldb.Column(String, nullable=False)  # path and name of file, where log were created
    level = psqldb.Column(String, nullable=False)  # info, debug, warn or error
    func_name = psqldb.Column(String, nullable=False)  # name of the function
    line_no = psqldb.Column(String, nullable=False)  # line number, where log were created
    msg = psqldb.Column(String, nullable=False)  # log msg (with exc_info, exc_text, exc_stack if there are)

    def __init__(self, pathname=None, level=None, func_name=None, line_no=None, msg=None):
        self.pathname = pathname
        self.level = level
        self.func_name = func_name
        self.line_no = line_no
        self.msg = msg

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Log: %s - %s>" % (self.created_at.strftime('%m/%d/%Y-%H:%M:%S'), self.msg[:50])


class Flight(psqldb.Model):
    __tablename__ = 'Flights'

    id = psqldb.Column(psqldb.BigInteger, unique=True, primary_key=True, nullable=False, autoincrement=True)
    number = psqldb.Column(psqldb.String(64))
    departure = psqldb.Column(psqldb.String(4))
    arrival = psqldb.Column(psqldb.String(4))
    departureTime = psqldb.Column(psqldb.TIMESTAMP)
    arrivalTime = psqldb.Column(psqldb.TIMESTAMP)
    airline = psqldb.Column(psqldb.String(256))

    def __init__(self, number, departure, arrival, departureTime, arrivalTime, airline):
        self.number = number
        self.departure = departure
        self.arrival = arrival
        self.departureTime = departureTime
        self.arrivalTime = arrivalTime
        self.airline = airline


class Airport(psqldb.Model):
    __tablename__ = 'Airports'

    id = psqldb.Column(psqldb.BigInteger, unique=True, primary_key=True, nullable=False, autoincrement=True)
    code = psqldb.Column(psqldb.String(64), unique=True, nullable=False)
    country = psqldb.Column(psqldb.String(256))
    city = psqldb.Column(psqldb.String(256))

    def __init__(self, code, country, city):
        self.code = code
        self.country = country
        self.city = city
