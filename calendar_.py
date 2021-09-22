
from config import*


#calendario con gli slot disponibili
calendar_ = Blueprint("calendar_",__name__, static_folder='static', template_folder='templates')

#funzione che restituisce in base a un cliente le sue prenotazioni
def slotPrenotati(id_cliente):
    cliente = Cliente.query.filter_by(id = id_cliente).first()
    return cliente.prenotazioni

#funzione che in base a un cliente mi restituisce tutti gli slot disponibili a cui
#deve ancora prenotarsi
def slotLiberi(id_cliente):
    l = []
    l_corsi = [] #lista di tutte le attivita
    
    for i in slotPrenotati(id_cliente):#lista slotdisponibili prenotati
        l.append(i.slot_disp.id)

    cliente = Cliente.query.filter_by(id = id_cliente).first()#cliente

    for c in cliente.corsi:#corsi_attivita del cliente
        l_corsi.append(c.attivita_id)
    for s in SalaPesi.query:#attivita salapesi
        l_corsi.append(s.attivita_id)
#l_corsi serve per mostrare i slot disponibili in relazioni con i corsi del cliente

    l2 = SlotDisponibile.query #select * from slotdisp    
    l_res = []
    for i in l2:
        if is_present(i.idattivita,l_corsi):
            if is_present(i.id,l):
                #già prenotata                
                    l_res.append(Prenot_cal(id = i.id, data = i.data, orainizio = i.slot.orainizio, orafine = i.slot.orafine, attivita = i.attivita.nome,flag = True ))
            else:
            #non è ancora prenotata
                l_res.append(Prenot_cal(id = i.id, data = i.data, orainizio = i.slot.orainizio, orafine = i.slot.orafine, attivita = i.attivita.nome))

    return l_res

#funzione is present
def is_present(x,list_):
    for i in list_:
        if i == x:
            return True
    else:
        return False

#classe prenotazione_calendario. Mi salva uno slot disponibile come un oggetto per poter avere il campo flag
class Prenot_cal():
    def __init__(self,id,data,orainizio,orafine,attivita,flag=False):
        self.id = id
        self.data = data
        self.orainizio = orainizio
        self.orafine = orafine
        self.attivita = attivita
        self.flag = flag #True = sono già iscritto, False = devo ancora iscrivermi

#prenotazione clienti
@app.route('/prenotazioni', methods=['GET', 'POST'])
def prenotazioni():
    #controlliamo che sia un cliente
    if not controlloIstr():             
        if request.method == 'POST': 
            #se passo una data       
            form_date = request.form['data']
            date = datetime.strptime(form_date,"%Y-%m-%d").date()
            #ritorna la lista delle prenotazioni
            list_p = slotPrenotati(current_user.id)    
            l = []
            #filtro solo prontazioni con la data giusta
            for p in list_p:
                if  p.slot_disp.data == date:
                    l.append(p)
            
            #passo la lista da visualizzare
            return render_template('prenotazioni.html',  lista_slot = l)
        else:
            #se non ho una data restituisco tutto
            list_p = slotPrenotati(current_user.id)    
            return render_template('prenotazioni.html',lista_slot = list_p)
        
    else:
        return redirect(url_for('index'))

#route che mi elimina le prenotazioni
@app.route('/elimina_prenotazione',methods=['GET', 'POST'])
def elimina_prenotazione():
    #controllo se è un cliente
    if not controlloIstr():   
        if request.method == 'POST':      
            #prendo l'ID della prenotazione da cancellare  
            pren_id = request.form['pren_id']
            #cerco e elimino prenotazione
            pren = Prenotazione.query.filter_by(id=pren_id).first()
            db.session.delete(pren)
            db.session.commit()            
        return redirect(url_for('prenotazioni'))
    else:
        return redirect(url_for('index'))

#gestiamo gli slot del calendario
@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    #controllo se è un cliente
    if not controlloIstr():             
        if request.method == 'POST':      
            #mi faccio passare una data  
            form_date = request.form['data']
            date = datetime.strptime(form_date,"%Y-%m-%d").date()
            #restituisco la lista di slot liberi
            list_p = slotLiberi(current_user.id)    
            l = []
            #filtro per data
            for p in list_p:
                if  p.data == date:
                    l.append(p)
            #passo la lista con gli slot liberi a cui posso iscrivermi
            return render_template('calendario.html',  lista_slot = l)
        else:
            #se non mi faccio passare una data stampo tutto
            list_p = slotLiberi(current_user.id)    
            return render_template('calendario.html',lista_slot = list_p)
        
    else:
        return redirect(url_for('index'))


#il cliente può iscriversi a corsi
@app.route('/add_prenotazione',methods=['GET', 'POST'])
def add_prenotazione():
    #controllo utente
    if not controlloIstr():   
        if request.method == 'POST':        
            #mi ritorna l'id dello slot
            slotp_id = request.form['slotp_id']
            #prenotazione di quel cliente con quello specifico slot_disp, lo creo
            pren = Prenotazione(idcliente = current_user.id, idslotdisponibili = slotp_id)
            #lo aggiungo
            db.session.add(pren)
            db.session.commit()            
        return redirect(url_for('calendar'))
    else:
        return redirect(url_for('index'))

#classe delle prenotazioni dei corsi  degli istruttori sugli slot
class Prenot_istr():
    def __init__(self,id,data,orainizio,orafine,attivita, num_part = 0):
        self.id = id
        self.data = data
        self.orainizio = orainizio
        self.orafine = orafine
        self.attivita = attivita
        self.num_part = num_part #aggiungo un campo in cui salvo il numero di partecipanti
        
#premotazioni ai corsi degli istruttori
@app.route('/istr_prenotazione')
def istr_prenotazione():
    #controllo se è un istruttore
    if controlloIstr():  
        #mi prendo l'istruttore 
        istr = Istruttore.query.filter_by(id = current_user.id).first()
        l = []
        #per ogni corso dell'istruttore
        for c in istr.corsi:
            #mi prendo i suoi slot_disp
            for i in c.attivita.slot_disp:
                #numero iscritti, i.prenotazioni = istr.corsi.attivita.slot_disp.prenotazioni
                p = len(i.prenotazioni)
                #creo l'oggetto
                new_pr = Prenot_istr(id = i.id, data = i.data, orainizio = i.slot.orainizio, orafine = i.slot.orafine, attivita = i.attivita.nome, num_part = p)
                #che appendo alla lista di ritorno che poi visualizzerò
                l.append(new_pr)
        return render_template('prenotaz_istrut.html', lista_slot = l)
    else:
        return redirect(url_for('index'))