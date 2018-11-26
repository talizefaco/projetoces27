import json
import socket
import _thread

# System parameters
host = "localhost"
port = 50001
backlog = 5
size = 1024

# Connections dictionary: keys are user names, values are connections to clients
connections = {}

def new_client(client, address):
    while True:
        raw_data = client.recv(size)
        if raw_data:
            # Decode the data
            data = json.loads(raw_data)
            print("SERVER >> Received:", data, "from", address)

            # If the data is of type connection, a client is requesting an user name
            # This verifies if the name has been taken already and, if not, adds it
            # to the connections dictionary
            if data["type"] == "connection":
                response = {}
                print("SERVER >>", address, "requested user name", data["payload"]["name"])
                if data["payload"]["name"] in connections:
                    response = {"type": "connection", "payload": {"status": "error"}}
                    print("SERVER >> Request from", address, "denied")
                else:
                    connections[data["payload"]["name"]] = client
                    response = {"type": "connection", "payload": {"status": "ok"}}
                    print("SERVER >> Request from", address, "granted")
                response = json.dumps(response)
                client.send(response.encode("utf-8"))
                print("SERVER >> Sent", response, "to", address)

            # If the data is of type message, a client is attempting to send a
            # message to another. For now, redirects it accordingly.
            elif data["type"] == "message":
                if data["payload"]["dest"] in connections:
                    connections[data["payload"]["dest"]].send(raw_data)
                    print("SERVER >> Sent", raw_data.decode("utf-8"), "to", data["payload"]["dest"])
                else:
                    print("SERVER >> User name", data["payload"]["dest"], "not registered")

            # If the data is of type broadcast, a client is attempting to send a
            # message to all the others clients.
            elif data["type"] == "broadcast":
                for user in connections:
                    if user != data["payload"]["source"]:
                        connections[user].send(raw_data)
                        print("SERVER >> Sent", raw_data.decode("utf-8"), "to", user)

            # If the data type is quit, the client wants to close the connection.
            # This is a client responsibility: only removes the client from the known hosts
            elif data["type"] == "quit":
                del connections[data["payload"]["source"]]
                print("SERVER >> Removed", data["payload"]["source"], "from connections")

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
