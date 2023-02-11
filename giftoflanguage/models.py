import datetime

import sqlalchemy
from giftoflanguage import database

if __name__ == '__main__':
    from config import DATABASEPASSWORD, DATABASENAME, HOST, USER
else:
    from giftoflanguage.config import DATABASEPASSWORD, DATABASENAME, USER, HOST
from sqlalchemy import create_engine, orm

Base = sqlalchemy.orm.declarative_base()

class TheUsers(Base):
    __tablename__ = 'the_users'

    UserID = database.Column(database.Integer, primary_key=True, autoincrement=True, nullable=False)
    FirstName = database.Column(database.String(65), nullable=False)
    LastName = database.Column(database.String(65), nullable=False)
    Email = database.Column(database.String(65), nullable=False, unique=True)
    DOB = database.Column(database.DateTime, nullable=False)
    City = database.Column(database.String(200), nullable=False)
    Username = database.Column(database.String(200), nullable=False)
    Password = database.Column(database.String(200), nullable=False)

    def __init__(self, FirstName, LastName, Email, DOB, City, Username, Password):
        self.FirstName = FirstName
        self.LastName = LastName
        self.Email = Email
        self.DOB = DOB
        self.City = City
        self.Username = Username
        self.Password = Password


class TheUsers(Base):
    __tablename__ = 'the_users'

    UserID = database.Column(database.Integer, primary_key=True, nullable=False, autoincrement=True)
    FirstName = database.Column(database.String(65), nullable=False)
    LastName = database.Column(database.String(65), nullable=False)
    Email = database.Column(database.String(255), unique=True)
    DOB = database.Column(database.DateTime, nullable=False)
    City = database.Column(database.String(65), nullable=False)
    Username = database.Column(database.String(65), unique=True)
    UserPassword = database.Column(database.String(65), nullable=False)
    LastLogin = database.Column(database.DateTime)
    UserStreak = database.Column(database.Integer)


class TheUsers(Base):
    __tablename__ = 'the_users'

    SearchedWordID = database.Column(database.Integer, primary_key=True, nullable=False, autoincrement=True)
    UserID = database.Column(database.Integer, database.ForeignKey('the_users.UserID'), nullable=False)
    word = database.Column(database.String(65), nullable=False)
    definition_ = database.Column(database.String(6000), nullable=False)
    date_accessed = database.Column(database.TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)

engine = create_engine("mysql+mysqlconnector://{user}:{password}@{host}/{DatabaseName}".format(
    user=USER,
    password=DATABASEPASSWORD,
    host=HOST,
    DatabaseName=DATABASENAME
))

Base.metadata.create_all(engine)



# db_name = 'GOL_users'

def _connect_to_db(db_name):
    # attribute
    connection = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        auth_plugin='mysql_native_password',
        database=db_name
    )
    return connection


def db_connection_decorator(func):
    def wrapper(*args):
        db_connection = None
        try:
            db_name = 'GOL_users'
            db_connection = _connect_to_db(db_name)
            cur = db_connection.cursor()
            result = func(*args, cur, db_connection)
            return result
            cur.close()
        except Exception:
            raise ConnectionError

        finally:
            if db_connection:
                db_connection.close()
                # print("DB connection closed")

    return wrapper



