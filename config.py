from itertools import count
from flask import Flask, render_template, redirect, url_for, flash, Blueprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from flask_sqlalchemy import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from wtforms.fields.html5 import DateField,DateTimeField 
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import query_expression
from sqlalchemy.sql.expression import null
from sqlalchemy import CheckConstraint
from sqlalchemy import DDL, event

app = Flask(__name__)

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!' #per le password     TODO: random
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/palestra1' #database

bootstrap = Bootstrap(app)

db = SQLAlchemy(app)#collegamento al DBMS

#istruzioni per il login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#istruzione per il login
@login_manager.user_loader
def load_user(id_):
    if(int(id_)<10000):#se l'ID minore di 10.000 allora è un cliente
        user = Cliente.query.filter_by(id = id_).first()
        if user:
            return Utente(user.id, user.nome, user.cognome, user.email, user.password)
    else: #altrimenti è un istruttore
        user = Istruttore.query.filter_by(id = id_).first()
        if user:
            return Utente(user.id, user.nome, user.cognome, user.email, user.password,  user.is_admin)    
    return None

#classe utente che può essere Cliente o Istruttore
class Utente(UserMixin):
    def __init__(self,id,nome, cognome, email,password, admin = False):
        self.id = id
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.password = password
        self.admin = admin
        

#controllo in base all'ID a chi mi riferisco se a cliente o istruttore
def controlloIstr():
    return current_user.is_authenticated and current_user.id >= 10000

def controlloAdmin():
    if controlloIstr:
        istr = Istruttore.query.filter_by(id = current_user.id).first()
        return istr.is_admin
    return False

#configurazione admin
admin = Admin(app, name='palestra', template_mode='bootstrap4')

#classi in relazione con le tabelle del DBMS
class Corso(db.Model): 
    __tablename__ = 'corsi'                  

    id = db.Column(db.Integer, primary_key=True)
    maxiscritti = db.Column(db.Integer, nullable=False)
    istruttore_id = db.Column(db.Integer, db.ForeignKey('istruttori.id'))   
    attivita_id = db.Column(db.Integer, db.ForeignKey('attivita.id'), nullable=False,unique = True)   
    
class Istruttore(db.Model): 
    __tablename__ = 'istruttori'                  

    id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=10000, increment=1),
               primary_key=True)
    nome = db.Column(db.String, nullable=False)
    cognome = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    datanasc = db.Column(db.Date, nullable=False)  
    is_admin = db.Column(db.Boolean, nullable=False)  

class Cliente(db.Model): 
    __tablename__ = 'clienti'                   

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    cognome = db.Column(db.String, nullable=False)
    email =db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    datanasc = db.Column(db.Date, nullable=False)

db.Table('iscrizioni',
    db.Column('cliente_id', db.Integer, db.ForeignKey('clienti.id'), primary_key=True),
    db.Column('corso_id', db.Integer, db.ForeignKey('corsi.id'), primary_key=True)
)

class Attivita(db.Model): 
    __tablename__ = 'attivita'                   

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    descrizione = db.Column(db.String) 


class SalaPesi(db.Model): 
    __tablename__ = 'salepesi'                   

    id = db.Column(db.Integer, primary_key=True)
    numattrezzi = db.Column (db.Integer)
    attivita_id = db.Column(db.Integer, db.ForeignKey('attivita.id'), unique = True, nullable = False) 

class SlotDisponibile(db.Model): 
    __tablename__ = 'slotdisponibili'                  

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    idslot = db.Column(db.Integer, db.ForeignKey('slots.id'), nullable=False) 
    idattivita = db.Column(db.Integer, db.ForeignKey('attivita.id'), nullable=False)

class Slot(db.Model): 
    __tablename__ = 'slots'                  

    id = db.Column(db.Integer, primary_key=True)
    orainizio = db.Column(db.Time, nullable=False)
    orafine = db.Column(db.Time, nullable=False)
    maxpersone = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default = True)

class Prenotazione(db.Model): 
    __tablename__ = 'prenotazioni'                  

    id = db.Column(db.Integer, primary_key=True)
    idcliente = db.Column(db.Integer, db.ForeignKey('clienti.id'))#todo pk
    idslotdisponibili = db.Column(db.Integer, db.ForeignKey('slotdisponibili.id'))#todo pk


Corso.attivita = db.relationship (Attivita, back_populates="corso")
#se cancello un'attività ovviamente cancello anche il corso
Attivita.corso = db.relationship (Corso, back_populates="attivita", cascade="all, delete")

SalaPesi.attivita = db.relationship (Attivita, back_populates="sala")
#se cancello un'attività cancello anche la sala pesi
Attivita.sala = db.relationship (SalaPesi, back_populates="attivita", cascade="all, delete")

Corso.istruttore = db.relationship (Istruttore, back_populates="corsi")

Prenotazione.slot_disp = db.relationship (SlotDisponibile, back_populates="prenotazioni")
Prenotazione.cliente = db.relationship (Cliente, back_populates="prenotazioni")

Slot.slot_disp = db.relationship (SlotDisponibile, order_by=SlotDisponibile.id,  back_populates="slot")
#se cancello un cliente cancello anche le sue prenotazioni
Cliente.prenotazioni = db.relationship (Prenotazione, order_by=Prenotazione.id,  back_populates="cliente", cascade="all, delete")

SlotDisponibile.attivita = db.relationship (Attivita, back_populates="slot_disp")
SlotDisponibile.slot=db.relationship(Slot, back_populates="slot_disp")
#se cancello uno slot disponibile cancello anche le sue prenotazioni
SlotDisponibile.prenotazioni=db.relationship(Prenotazione, order_by=Prenotazione.id, back_populates="slot_disp", cascade="all, delete")

Attivita.slot_disp = db.relationship (SlotDisponibile, order_by=SlotDisponibile.id,  back_populates="attivita")

Istruttore.corsi = db.relationship (Corso, order_by=Corso.id, back_populates="istruttore")

Cliente.corsi = db.relationship("Corso", "iscrizioni", back_populates="clienti")
Corso.clienti = db.relationship("Cliente", "iscrizioni", back_populates="corsi")

db.create_all()