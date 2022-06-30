import json
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5559")


#Provjera koliko je novaca u bankomatu
with open("stanjeNaBankomatu.json", 'r') as file:
    stanje = file.read()
if not isinstance(stanje, int):
    stanje = int(stanje)

#print("Stanje na bankomatu iznosi: ", stanje)

while True:
    brojKartice = input("Unesite broj kartice:")
    pin = input("Unesite PIN:")
    if len(brojKartice) == 16 and brojKartice.isdigit():
        if len(pin) == 4 and pin.isdigit():
            print("Uspješan unos broja kartice i PIN-a.")

        print ("1 - Iznos stanja na racunu\n2 - Isplata\nBilo koja druga tipka za prekid")
        odabir = int(input("Vas odabir: "))
        if odabir == 1:
            dict = {"BrojKartice": brojKartice, "PIN": pin, "Radnja": "stanje"}
            # json dumps za pretvaranje dictionaria u string
            socket.send_string(json.dumps(dict))
            msg = socket.recv_string()
            # json loads pretvara string u dictionary
            msg = json.loads(msg)
            # print treba jer tu dobivamo iznos
            print(msg.get("msg"))
            # continue da bi sljedeci korinsik mogao upotrijebiti bankomat
            continue
        # ako je odabir 1 vec smo izvrsili sto je trebalo
        # tako da provjeravamo ako je odgovor razlicit od 2
        # ako je preskacemo sve, ako nije izvrsavamo glavni kod za isplatu
        if odabir != 2:
            continue
        print("1 - 100 kn\n2 - 200 kn\n3 - 300 kn\n4 - 400 kn\n5 - 500 kn\n6 - 1000 kn\n7 - 2000 kn\n8 - 5000 kn\n9 - Upišite iznos:")
        iznos = int(input("Odaberite koliko novca želite podići s kartice broj {}:".format(brojKartice)))

        if iznos == 1 and stanje >= 100:
            iznos_isplate = 100
        elif iznos == 2 and stanje >= 200:
            iznos_isplate = 200
        elif iznos == 3 and stanje >= 300:
            iznos_isplate = 300
        elif iznos == 4 and stanje >= 400:
            iznos_isplate = 400
        elif iznos == 5 and stanje >= 500:
            iznos_isplate = 500
        elif iznos == 6 and stanje >= 1000:
            iznos_isplate = 1000
        elif iznos == 7 and stanje >= 2000:
            iznos_isplate = 2000
        elif iznos == 8 and stanje >= 5000:
            iznos_isplate = 5000
        elif iznos == 9:
            drugiIznos = int(input("Upišite samostalno iznos koji želite podići:"))
            if drugiIznos % 100 == 0 and drugiIznos <= int(stanje):
                iznos_isplate = drugiIznos
            else:
                print("Nepravilan unos.")
                continue
            
        print(f"Podizanje {iznos_isplate} kn...")
        dict = {"BrojKartice": brojKartice, "PIN": pin, "Iznos": iznos_isplate, "Radnja": "isplata"}
        socket.send_string(json.dumps(dict))
        msg = socket.recv_string()
        msg = json.loads(msg)
        if msg.get("msg") == "ok":
            novoStanje = stanje - int(iznos_isplate)
            novoStanje = str(novoStanje)
            with open("stanjeNaBankomatu.json", "w") as data:
                data.write(novoStanje)
        else:
            print("Zao nam je, doslo je do pogreske")
            print(msg.get("msg"))

    else:
        print("Neispravan unos broja kartice i/ili PIN-a.\nBroj kartice sastoji se od 16 brojeva, a PIN od 4 broja.")
        continue