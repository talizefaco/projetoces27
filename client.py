import json
import socket
import os
import _thread

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
        print("User name for direct message, b for broadcast or q for quiting")
        dest = input()
        if dest == "q":
            print("Bye")
            data = json.dumps({"type": "quit", "payload": {"source": name}})
            s.send(data.encode("utf-8"))
            s.close()
            # Need to use os instead of sys, because sys only stops the thread
            os._exit(0)

        print("What is the message?")
        msg = input()
        if dest == "b":
            data = json.dumps({"type": "broadcast", "payload": {"source": name, "content": msg}})
        else:
            data = json.dumps({"type": "message", "payload": {"source": name, "dest": dest, "content": msg}})
        s.send(data.encode("utf-8"))

# Request an user name (must be unique in the system)
print("What name do you want to use?")
while True:
    name = input()
    if name == "b" or name == "q":
        print("Reserved name. Try another one")
        continue
    data = json.dumps({"type": "connection", "payload": {"name": name}})
    s.send(data.encode("utf-8"))
    # Waits for server response
    data = s.recv(size)
    if data:
        data = json.loads(data.decode("utf-8"))
        # Ok status means the name has been accepted
        if data["payload"]["status"] == "ok":
            break
        else:
            print("Name already taken. Try another one.")

_thread.start_new_thread(send_message, ())

while True:
    raw_data = s.recv(size)
    if raw_data:
        data = json.loads(raw_data.decode("utf-8"))
        if data["type"] == "broadcast":
            print(data["payload"]["source"], "(broadcast) >>", data["payload"]["content"])
        elif data["type"] == "message":
            print(data["payload"]["source"], ">>", data["payload"]["content"])
        else:
            print("Something wrong has happened, tell about this to the system admin!")
            print("And send him this:", raw_data)
            os._exit(1)

# Close the connection
s.close()
