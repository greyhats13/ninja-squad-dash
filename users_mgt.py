from sqlalchemy import Table
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from config import engine

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    fullname = db.Column(db.String(120))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    confirmkey = db.Column(db.String(80))
    last_login = db.Column(db.String(80))

User_tbl = Table('user', User.metadata)


def create_user_table():
    User.metadata.create_all(engine)


def add_user(fullname, username, password, email):
    hashed_password = generate_password_hash(password, method='sha256')

    ins = User_tbl.insert().values(
        fullname=fullname, username=username, email=email, password=hashed_password)

    conn = engine.connect()
    conn.execute(ins)
    conn.close()

def get_token(email, token):
    updtoken = User_tbl.update().where(User_tbl.c.email == email).values(confirmkey=token)

    conn = engine.connect()
    conn.execute(updtoken)
    conn.close()

def delete_token(email, waktu):
    updtoken = User_tbl.update().where(User_tbl.c.email == email).values(confirmkey=None, last_login=waktu)

    conn = engine.connect()
    conn.execute(updtoken)
    conn.close()

def change_password(username, password):
    hashed_password = generate_password_hash(password, method='sha256')

    updpw = User_tbl.update().where(User_tbl.c.username == username).values(password=hashed_password)

    conn = engine.connect()
    conn.execute(updpw)
    conn.close()

def del_user(username):
    delete = User_tbl.delete().where(User_tbl.c.username == username)

    conn = engine.connect()
    conn.execute(delete)
    conn.close()


def show_users():
    select_st = select([User_tbl.c.fullname, User_tbl.c.username]).where(User_tbl.c.username!='admin')

    conn = engine.connect()
    rs = conn.execute(select_st)

    userlist = [((row[0]+" ("+row[1]+")",row[1])) for row in rs]
    conn.close()

    return userlist

def list_users():
    select_st = select([User_tbl.c.username]).where(User_tbl.c.username!='admin')

    conn = engine.connect()
    rs = conn.execute(select_st)

    userlist = [(row[0]) for row in rs]
    conn.close()

    return userlist

def send_reminder():
    select_sr = select([User_tbl.c.fullname, User_tbl.c.email, User_tbl.c.last_login, User_tbl.c.confirmkey]).where(User_tbl.c.email!='muhamad.mustain@ninjavan.co')

    conn = engine.connect()
    rs = conn.execute(select_sr)

    receiver = [(row[0], row[1], row[2], row[3]) for row in rs]
    conn.close()

    return receiver
