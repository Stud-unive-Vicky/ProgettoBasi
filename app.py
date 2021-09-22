from config import*
from auth import*
from adminB import*
from signup import*
from views import *
from calendar_ import *

#pagina autentucazione clienti e istruttori, e registrazione cliente
app.register_blueprint(auth, url_prefix = '/auth')   
#pagina iscrizione di un istruttore
app.register_blueprint(signupI, url_prefix = '/signupIstr')   #todo vista solo admin
#pagina admin
app.register_blueprint(adminB) 
#pagina viste corsi clienti e istruttori
app.register_blueprint(views,  url_prefix = '/views') 
#pagina calendario e prenotazioni, per clienti e istruttori
app.register_blueprint(calendar_,url_prefix = '/calendar')


@app.route('/')
def index():
    if current_user.is_authenticated:
        #se è loggato
        return render_template('dashboard.html')
    else:
        #se non è loggato
        return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():    
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)