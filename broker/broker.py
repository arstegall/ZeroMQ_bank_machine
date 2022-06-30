import json
import uuid
import zmq

from time import time, ctime

# Pripremamo zmq
context = zmq.Context()
frontend = context.socket(zmq.ROUTER)
backend = context.socket(zmq.DEALER)
frontend.bind("tcp://*:5559")
backend.bind("tcp://*:5560")

poller = zmq.Poller()
poller.register(frontend, zmq.POLLIN)
poller.register(backend, zmq.POLLIN)

req_logs = open("request_logs.txt", "a")
res_logs = open("response_logs.txt", "a")


def check_error_in_dict(message):
    if message.get("status_code") == 500:
        print("\033[1m" + "***** SERVER ERROR *****")
        print(message)
        print(80*"*")
        return True
    for value in message.values():
        if "error" in value:
            print("\033[1m" + "***** SERVER ERROR *****")
            print(message)
            print(80*"*")
            return True
    return False

def check_for_server_errors(message):
    try:
        if isinstance(message, bytes):
            try:
                message = message.decode()
            except:
                message = str(message)
        if isinstance(message, dict):
            if check_error_in_dict(message):
                return
        if isinstance(message, list):
            for item in message:
                if isinstance(item, bytes):
                    try:
                        item = item.decode()
                    except:
                        item = str(item)
                if isinstance(item, dict):
                    if check_error_in_dict(item):
                        return
                if isinstance(item, str):
                    if "error" in item:
                        print("\033[1m" + "***** SERVER ERROR *****")
                        print(item)
                        print(80*"*")
                        return
            if isinstance(message, str):
                if "error" in message:
                    print("\033[1m" + "***** SERVER ERROR *****")
                    print(message)
                    print(80*"*")
                    return
    except Exception as e:
        print(f"Error while checking for server errors: {e}")


def save_logs(file, message, check_errors = False):
    log_id =  uuid.uuid4().hex
    real_time = ctime()     # human readable time
    unix_time = time()
    message_type = type(message)
    if isinstance(message, bytes):
        try:
            message = message.decode()
        except:
            message = str(message)
    if check_errors:
        check_for_server_errors(message)
    log_format = {
        "id": log_id,
        "time": real_time,
        "unix_time": unix_time,
        "message_type": str(message_type),
        "message": str(message)
    }
    log_format = json.dumps(log_format)
    file.write(log_format)
    
    


# Switch messages between sockets
while True:
    socks = dict(poller.poll())

    if socks.get(frontend) == zmq.POLLIN:
        message = frontend.recv_multipart()
        backend.send_multipart(message)
        save_logs(req_logs, message)

    if socks.get(backend) == zmq.POLLIN:
        message = backend.recv_multipart()
        frontend.send_multipart(message)
        save_logs(res_logs, message, check_errors=True)
