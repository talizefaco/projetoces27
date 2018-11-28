import json
import socket
import os
import _thread
import time
import random
import numpy as np
from copy import deepcopy
from os import system

# System parameters
host = "localhost"
port = 50001
size = 1024

# Create connection to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
id = ""

# Le arquivo txt e salva em uma matriz de char
n_linhas = 40
n_colunas = 120
dim = (n_linhas, n_colunas)
mapa_original = np.chararray(dim)
with open("map.txt") as f:
    i = 0
    j = 0
    while True:
        c = f.read(1)
        if not c:
            break
        if c != '\n':
            mapa_original[i][j] = c
            j = j + 1
        else:
            i = i + 1
            j = 0
mapa = deepcopy(mapa_original)

# Movimento aleatório do usuário
def movimenta(p):
    x = p[0]
    y = p[1]
    x_antes = x
    y_antes = y

    falhou = False
    while (x_antes == x and y_antes == y):
        cont = 0
        if mapa_original[x-1][y] == b'0':
            cont = cont+1
        if mapa_original[x+1][y] == b'0': 
            cont = cont+1
        if mapa_original[x][y-1] == b'0':
            cont = cont+1
        if mapa_original[x][y+1] == b'0':
            cont = cont+1

        rnd = random.random()
        if cont <= 2 and falhou == False:
            rnd = p[2]
        
        #cima
        if rnd < 0.25:
            if mapa_original[x-1][y] == b'0':
                x = x - 1
        #baixo
        elif rnd < 0.5:
            if mapa_original[x+1][y] == b'0': 
                x = x + 1
        #esquerda
        elif rnd < 0.75:
            if mapa_original[x][y-1] == b'0':
                y = y - 1
        #direita
        else:
            if mapa_original[x][y+1] == b'0': 
                y = y + 1
        falhou = True
    return x, y, rnd

def send_localization():
    # Initial Localization
    x0 = random.randint(0, n_linhas-1)
    y0 = random.randint(0, n_colunas-1)

    while mapa_original[x0][y0]!=b'0':
        x0 = random.randint(0, n_linhas-1)
        y0 = random.randint(0, n_colunas-1)
    p = (x0, y0, random.random())

    #Manda a localizacao com o id e movimenta
    while True:
        local = p
        p = movimenta(p)
        data = json.dumps({"type": "localization", "payload": {"source": id, "content": local}})
        s.send(data.encode("utf-8"))
        print("Localization: ", local)
        time.sleep(3)
        
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

_thread.start_new_thread(send_localization, ())

while True:
    raw_data = s.recv(size)
    if raw_data:
            print("Something wrong has happened, tell about this to the system admin!")
            print("And send him this:", raw_data)
            os._exit(1)

# Close the connection
s.close()
