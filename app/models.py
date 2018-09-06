from app import psqldb, arangodb
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return Users.query.get(id)


class Users(psqldb.Model, UserMixin):
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


class Flight(psqldb.Model):
    __tablename__ = 'flights'

    id = psqldb.Column(psqldb.BigInteger, unique=True,  primary_key=True, nullable=False, autoincrement=True)
    number = psqldb.Column(psqldb.String(64))
    departure = psqldb.Column(psqldb.String(4))
    arrival = psqldb.Column(psqldb.String(4))
    departureTime = psqldb.Column(psqldb.TIMESTAMP)
    arrivalTime = psqldb.Column(psqldb.TIMESTAMP)
    airline = psqldb.Column(psqldb.String(256))
    price = psqldb.Column(psqldb.Float)

    def __init__(self, id, number, departure, arrival, departureTime, arrivalTime, airline, price):
        self.id = id
        self.number = number
        self.departure = departure
        self.arrival = arrival
        self.departureTime = departureTime
        self.arrivalTime = arrivalTime
        self.airline = airline
        self.price = price
