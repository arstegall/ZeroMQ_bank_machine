import json
import zmq

from datetime import date

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5560")

# ucitavanje datoteke sa korisnickim podacima
# biti ce potrebno u svakoj iteraciji
with open("users_db.json", "r") as data:
    users_data = data.read()
users_data = json.loads(users_data)


# funkcija vraca string u json obliku
# namijenjeno za formatiranje odgovora
def odgovor(msg, response_code = 200):
    return json.dumps({"msg": msg, "response_code": response_code})


def isplata(message, users_data, user):
    try:
        if int(message["Iznos"]) > int(user["stanje_racuna"]):
            print("Nedovoljno sredstava")
            socket.send_string(odgovor("Nemate dovoljno sredstava na racunu"))
            return

        # podaci za azuriranje stanja racuna
        # i potencijalno vracanje na izvorni iznos
        staro_stanje_racuna = int(user["stanje_racuna"])
        user["stanje_racuna"] -= int(message["Iznos"])
        users_data[message["BrojKartice"]] = user

        try:
            # azuriramo stanje racuna
            with open("users_db.json", "w") as data:
                data.write(json.dumps(users_data))
        except Exception as e:
            print(f"Error updating db: {e}")
            socket.send_string(odgovor("Transakcija neuspijesna", 500))
            return

        try:
            socket.send_string(odgovor("ok"))
        except Exception as e:
            # vracanje stanja racuna na pocetni iznos
            print(e)
            user["stanje_racuna"] = staro_stanje_racuna
            users_data[message["BrojKartice"]] = user
            with open("users_db.json", "w") as data:
                data.write(json.dumps(users_data))
            return
    except Exception as e:
        print(e)
        socket.send_string(odgovor("Internal server error", 500))


def stanje(user):
    msg = f"Postovani {user['ime']} {user['prezime']}, Vase stanje racuna na dan {date.today().strftime('%d/%m/%Y')} iznosi: {user['stanje_racuna']} kn"
    socket.send_string(odgovor(msg))

while True:
    message = socket.recv_string()
    try:
        # iz stringa radimo dict
        message = json.loads(message)
        # provjera ako zaprimljeni zahtjev sadrzi sve potrebne podatke
        if (
            not message.get("BrojKartice")
            or not message.get("PIN")
        ):
            raise ValueError(f"Nedostaju podaci u zahtjevu: {message}")
        if message.get("Radnja") == "isplata" and not message.get("Iznos"):
            raise ValueError("Nedostaje iznos za isplatu")
        if message.get("Radnja") not in ["isplata", "stanje"]:
            raise ValueError("Nepostojeca radnja")
    except Exception as e:
        print(f"Can not load message. Error: {e}")
        socket.send_string(odgovor("Pogresan zahtjev. Provjerit upisane podatke", 400))
        continue

    user = users_data.get(message["BrojKartice"])
    if not user:
        print("Broj kartice nije pronaden")
        socket.send_string(odgovor("Broj kartice nije pronaden", 404))
        continue

    if message["PIN"] != user["pin"]:
        print("Krivi pin")
        socket.send_string(odgovor("Krivi pin!", 403))
        continue

    if user["blokiran"]:
        print("Racun blokiran")
        socket.send_string(odgovor("Racun je blokiran", 403))
        continue

    if message.get("Radnja") == "isplata":
        isplata(message, users_data, user)
    else:
        stanje(user)
