import json
import socket
import os
import _thread
import time

# System parameters
host = "localhost"
port = 50001
size = 1024

# Create connection to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
name = ""

def send_message():
    while True:
        print("Localization")
        local = input() #NAO VAI SER INPUT, VAI SER A LOCALIZACAO
        data = json.dumps({"type": "localization", "payload": {"source": id, "content": local}})
        s.send(data.encode("utf-8"))

# Request an user ID (must be unique in the system)
print("What ID do you want to use?")
while True:
    id = input()
    data = json.dumps({"type": "connection", "payload": {"id": id}})
    s.send(data.encode("utf-8"))
    # Waits for server response
    data = s.recv(size)
    if data:
        data = json.loads(data.decode("utf-8"))
        # Ok status means the ID has been accepted
        if data["payload"]["status"] == "ok":
            break
        else:
            print("ID already taken. Try another one.")

_thread.start_new_thread(send_message, ())

while True:
    raw_data = s.recv(size)
    if raw_data:
            print("Something wrong has happened, tell about this to the system admin!")
            print("And send him this:", raw_data)
            os._exit(1)

# Close the connection
s.close()
