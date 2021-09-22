from config import*

#CORSI
views = Blueprint("views",__name__, static_folder='static', template_folder='templates')
        
#mostra i corsi dell'istruttore che deve gestire
@app.route('/corsoIstr')
def corsoIstr():
    #controllo se è un istruttore
    if controlloIstr():  
        istr = Istruttore.query.filter_by(id = current_user.id).first() #istruttore
        istrC = istr.corsi
        #ritorno la lista con i suoi corsi
        return render_template('corsi.html', istr = istrC)
    else:
        return redirect(url_for('index'))

#iscritti al corso di quel specifico istruttore
@app.route('/info_corso', methods=['GET', 'POST'])
def info_corso():
    #controllo se è un istruttore
    if controlloIstr():  
        if request.method == 'POST':        
            #corso specifico
            corso_id = request.form['corso_id']
            corso = Corso.query.filter_by(id = corso_id).first() #cerco il corso
            #ritorno i clienti iscritti a quel corso specifico
            return render_template('info_corsi.html', corso = corso.attivita.nome, clienti = corso.clienti)        
    
    return redirect(url_for('index'))

#mostra i corsi a cui è iscritto il cliente e a cui non lo è per aggiungerli
@app.route('/corsoClnt')
def corsoClnt():
    #controllo se è un cliente
    if not controlloIstr(): 
        clnt = Cliente.query.filter_by(id = current_user.id).first() #cliente specifico
        #invio anche i corsi a cui non è iscritto, così da potersi iscriversi con il bottone
        corsi = set(Corso.query) #lista corsi
        corsi_clnt = set(clnt.corsi) #lista corsi di quel specifico cliente
        corsi2 = corsi - corsi_clnt 
        add_corsi = list(corsi2) #lista corsi a cui non è iscritto
        
        return render_template('corsi_clnt.html', lista_corsi = clnt.corsi, add_corsi = add_corsi)
    else:
        return redirect(url_for('index'))

#gestire l'aggiunta di corsi a un cliente
@app.route('/add_corso', methods=['GET', 'POST'])
def add_corso():
    #controllo che sia un cliente
    if not controlloIstr(): 
        if request.method == 'POST':  
            #per un determinato corso che faccio submit      
            corso_id = request.form['corso_id']
            #aggiungi corso al cliente
            clnt = Cliente.query.filter_by(id = current_user.id).first() #cliente specifico
            corso = Corso.query.filter_by(id = corso_id).first() #corso specifico
            clnt.corsi.append(corso) #aggiungo
            db.session.commit()
        #ritorna alla pagina corsi dei clienti
        return redirect(url_for('corsoClnt'))
    else:
        return url_for('/index')

#elimina corso di un cliente
@app.route('/elimina_corso', methods=['GET', 'POST'])
def elimina_corso():
    #se è un cliente
    if not controlloIstr(): 
        if request.method == 'POST':        
            corso_id = request.form['corso_id']
            #rimuovo corso al cliente
            clnt = Cliente.query.filter_by(id = current_user.id).first() #cliente specifico
            corso = Corso.query.filter_by(id = corso_id).first() #corso specifico
            clnt.corsi.remove(corso) #rimuovo
            db.session.commit()
        return redirect(url_for('corsoClnt'))
    else:
        return redirect(url_for('index'))