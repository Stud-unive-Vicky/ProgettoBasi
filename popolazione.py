from  config import*

def popCorsi():
    db.session.add_all([Corso(maxiscritti=3, attivita_id = 34 , istruttore_id = 10000),#16
                    Corso( maxiscritti=2, attivita_id = 35 , istruttore_id = 10000),#17
                    Corso(maxiscritti=1, attivita_id = 37 , istruttore_id =  10001)])#18
    db.session.commit()

def popAtt():
    db.session.add_all([Attivita(nome='PILATES'),#34
                    Attivita(nome='YOGA'),#35
                    Attivita(nome='LOL'),#36
                    Attivita(nome='SALA1'),#37
                    Attivita(nome='SALA2')])#38
    db.session.commit()

def popSalaPesi():
    db.session.add_all([SalaPesi(attivita_id=37),#2
                    SalaPesi(attivita_id=38)])#3
    db.session.commit()

def popSlotDisp():
    db.session.add_all([
        SlotDisponibile(data = '2021-09-01',idslot = 1, idattivita=37),#20
        SlotDisponibile(data = '2021-09-01',idslot = 2, idattivita=38),#21
        SlotDisponibile(data = '2021-09-01',idslot = 3, idattivita=38),#22
        SlotDisponibile(data = '2021-09-01',idslot = 3, idattivita=34),#23
        SlotDisponibile(data = '2021-09-02',idslot = 8, idattivita=34),#24
        SlotDisponibile(data = '2021-09-02',idslot = 8, idattivita=35),#25
        SlotDisponibile(data = '2021-09-03',idslot = 3, idattivita=36),#26
        SlotDisponibile(data = '2021-09-02',idslot = 4, idattivita=35),#27
        ])
        
    db.session.commit()



