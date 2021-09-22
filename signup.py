from inspect import cleandoc
from sqlalchemy.engine import url
from config import*
from wtforms import BooleanField as WTBool

#registrazione dell'istruttore
signupI = Blueprint("signupI",__name__, static_folder='static', template_folder='templates')

class RegisterFormIstr(FlaskForm):
    nome = StringField('nome', validators=[InputRequired(), Length(min=4, max=15)])
    cognome = StringField('cognome', validators=[InputRequired(), Length(min=4, max=15)])
    email = StringField('email', validators=[InputRequired(),  Length(max=50)])
    date = StringField('data di nascita', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)])
    checkbox = BooleanField('admin')

class RegisterFormClnt(FlaskForm):
    nome = StringField('nome', validators=[InputRequired(), Length(min=4, max=15)])
    cognome = StringField('cognome', validators=[InputRequired(), Length(min=4, max=15)])
    email = StringField('email', validators=[InputRequired(),  Length(max=50)])
    date = StringField('data di nascita', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)])

def controllo_email(email):
    clienti = Cliente.query
    istruttori = Istruttore.query
    l = []
    for c in clienti:
        l.append(c.email)
    for i in istruttori:
        l.append(i.email)
    return is_present(email, l)

    #funzione is present
def is_present(x,list_):
    for i in list_:
        if i == x:
            return True
    else:
        return False

@app.route('/signupIstr', methods=['GET', 'POST'])
def signupIs():
    if controlloAdmin():
        form = RegisterFormIstr()

        if form.validate_on_submit():
            hash = generate_password_hash(form.password.data)
            admin = form.checkbox.data
            if controllo_email(form.email.data):
                return render_template('signupIstr.html', form=form, text = 'email esiste già')
            new_user = Istruttore(nome = form.nome.data,cognome=form.cognome.data, datanasc=form.date.data, email=form.email.data, password=hash, is_admin = admin)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))
        else: 
            return render_template('signupIstr.html', form=form)
    return  redirect(url_for('index'))

#registrazione di un cliente
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterFormClnt()

    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        if controllo_email(form.email.data):
            return render_template('signup.html', form=form, text = 'email esiste già')
        new_user = Cliente(nome=form.nome.data,cognome=form.cognome.data, datanasc=form.date.data, email=form.email.data, password=hash)
        db.session.add(new_user)
        db.session.commit()   
        return redirect(url_for('login')) 

    return render_template('signup.html', form=form)
