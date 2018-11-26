import json
import socket
import _thread

# System parameters
host = "localhost"
port = 50001
backlog = 5
size = 1024

# Connections dictionary: keys are user IDs, values are connections to clients
connections = {}

def new_client(client, address):
    while True:
        raw_data = client.recv(size)
        if raw_data:
            # Decode the data
            data = json.loads(raw_data)
            print("SERVER >> Received:", data, "from", address)

            # If the data is of type connection, a client is requesting an ID
            # This verifies if the ID has been taken already and, if not, adds it
            # to the connections dictionary
            if data["type"] == "connection":
                response = {}
                print("SERVER >>", address, "requested user ID", data["payload"]["id"])
                if data["payload"]["id"] in connections:
                    response = {"type": "connection", "payload": {"status": "error"}}
                    print("SERVER >> Request from", address, "denied")
                else:
                    connections[data["payload"]["id"]] = client
                    response = {"type": "connection", "payload": {"status": "ok"}}
                    print("SERVER >> Request from", address, "granted")
                response = json.dumps(response)
                client.send(response.encode("utf-8"))
                print("SERVER >> Sent", response, "to", address)

            # If the data is of type localization, a client is attempting to send his localization to the server.
            elif data["type"] == "localization":
                print(data["payload"]["content"])
            
            #PRA TIRAR O CLIENT:        
            #del connections[data["payload"]["source"]]
            #print("SERVER >> Removed", data["payload"]["source"], "from connections")

            # No other types of data are allowed! (should not happen)
            else:
                print("SERVER >> Invalid message type received from", address)
                response = json.dumps({"type": "error", "payload": {"message": "Invalid data type"}})
                client.send(response.encode("utf-8"))
                print("SERVER >> Sent", response, "to", address)

print("SERVER >> Starting server on port", port)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)
print("SERVER >> Waiting for connections")

while True:
    client, address = s.accept()
    print("SERVER >> Accepted connection from", address)
    _thread.start_new_thread(new_client, (client, address))
s.close()
