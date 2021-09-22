from sqlalchemy.engine import url
from sqlalchemy.sql.expression import false
from config import*

adminB = Blueprint("adminB",__name__, static_folder='static', template_folder='templates')

class MyModelView(ModelView):
    def is_accessible(self):    #controllo accesso
        return controlloAdmin()

    def inaccessible_callback(self, name, **kwargs):        # se non vi può accedervi
        return redirect(url_for('login'))

#lista viste
admin.add_view(MyModelView(Cliente, db.session, name='Utenti'))
admin.add_view(MyModelView(Istruttore, db.session, name='Istruttori'))
admin.add_view(MyModelView(Corso, db.session, name='Corsi'))
admin.add_view(MyModelView(SalaPesi, db.session, name='Salapesi'))
admin.add_view(MyModelView(Attivita, db.session, name='Attivita'))
admin.add_view(MyModelView(Prenotazione, db.session, name='Prenotazione'))
admin.add_view(MyModelView(SlotDisponibile, db.session, name='SlotDisponibile'))
admin.add_view(MyModelView(Slot, db.session, name='Slot'))


#tracking dei slot disponibili e il numero di prenotazioni
@app.route("/tracking", methods=['GET', 'POST'])
def tracking():
    if controlloAdmin():
        if request.method == 'POST':      
            #mi faccio passare una data  
            form_date = request.form['data']
            date = datetime.strptime(form_date,"%Y-%m-%d").date()
            
            list_p = SlotDisponibile.query   #restituisce la lista di slot liberi
            l = []
            #filtro per data
            for p in list_p:
                if  p.data == date:
                    l.append(p)
            #ritorno la lista con gli SlotDisponibili
            return render_template('tracking.html', list_p = l)
        else:
            #se non ho scelto una data
            list_slot = SlotDisponibile.query
            return render_template('tracking.html', list_p = list_slot)
    else:
        return redirect(url_for('index'))

#clienti presenti in quello slot
@app.route("/tracking_clienti", methods=['GET', 'POST'])
def tracking_clienti():
    if controlloAdmin:
        if request.method == 'POST':   
            #prendo l'id dell SlotDisponibili
            slot_id = request.form['slot_id']  
            slot = SlotDisponibile.query.filter_by(id = slot_id).first() #cerco lo slot disponibile
            #passo la lista delle prenotazioni riferite a quello slot
            return render_template('tracking_clienti.html', list_c = slot.prenotazioni)

    return redirect(url_for('tracking'))

        