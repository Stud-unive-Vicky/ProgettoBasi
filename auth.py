from config import*

#login istruttori e clienti, registrazione cliente
auth = Blueprint("auth",__name__, static_folder='static', template_folder='templates')

#form per il login
class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)])
    remember = BooleanField('remember me')



#login Cliente-Istruttore
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    #se è già autenticato, ritorna alla pagina dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if form.validate_on_submit():
        
        user = Cliente.query.filter_by(email=form.email.data).first()        #cerco il cliente
        if user:            #controllo del Cliente se esiste
            u = Utente(user.id, user.nome, user.cognome, user.email, user.password)        
            if check_password_hash(user.password, form.password.data):#controllo password
                login_user(u, remember=form.remember.data)
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', form=form, text = 'password o email sbagliata')
        else:            #controllo dell'Istruttore se esiste
            user = Istruttore.query.filter_by(email=form.email.data).first()            
            if user:
                u = Utente(id = user.id, nome = user.nome, cognome = user.cognome, 
                email = user.email, password = user.password, admin = user.is_admin)
                if check_password_hash(user.password, form.password.data):#controllo password
                    login_user(u, remember=form.remember.data)
                    return redirect(url_for('dashboard'))

                else:
                    return render_template('login.html', form=form, text = 'password o email sbagliata')
        

    return render_template('login.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

