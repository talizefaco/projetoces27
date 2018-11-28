import json
import socket
import _thread
import random
import time
import numpy as np
from copy import deepcopy
from os import system

# System parameters
host = "localhost"
port = 50001
backlog = 5
size = 1024

# Connections dictionary: keys are user IDs, values are connections to clients
connections = {}

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

# Matriz de inteiros que indica posicoes mais percorridas
mapaint = np.zeros(dim)
for i in range(0, n_linhas):
    for j in range(0, n_colunas):
        if mapa_original[i][j] != b'0':
            mapaint[i][j] = -1

# Acende um bloco de "n_em_volta" casas em todas as direções da posicao
def acende_luzes_em_volta(p, cont):
    global mapa
    if cont >= 1:
        if mapa[p[0] - 1][p[1]] == b'0':
            mapa[p[0] - 1][p[1]] = b'+'
            acende_luzes_em_volta((p[0] - 1, p[1]), cont - 1)
        if mapa[p[0] + 1][p[1]] == b'0':
            mapa[p[0] + 1][p[1]] = b'+'
            acende_luzes_em_volta((p[0] + 1, p[1]), cont - 1)
        if mapa[p[0]][p[1] - 1] == b'0': 
            mapa[p[0]][p[1] - 1] = b'+' 
            acende_luzes_em_volta((p[0], p[1] - 1), cont - 1)
        if mapa[p[0]][p[1] + 1] == b'0':
            mapa[p[0]][p[1] + 1] = b'+'  
            acende_luzes_em_volta((p[0], p[1] + 1), cont - 1)

# Acende o caminho mais percorrido a partir daquela posicao
def acende_luzes_caminho_otimizado(p, cont):
    global mapa
    global mapaint
    sentido = "cima"
    maior = mapaint[p[0]-1][p[1]]

    #baixo
    if maior < mapaint[p[0]+1][p[1]]:
        sentido = "baixo"
        maior = mapaint[p[0]+1][p[1]]

    #esquerda
    if maior < mapaint[p[0]][p[1]-1]:
        sentido = "esquerda"
        maior = mapaint[p[0]][p[1]-1]

    #direita
    if maior < mapaint[p[0]][p[1]+1]:
        sentido = "direita"
        maior = mapaint[p[0]][p[1]+1]

    if cont >= 1:
        if sentido == "cima":
            if mapa[p[0] - 1][p[1]] != b'P':
                mapa[p[0] - 1][p[1]] = b'+'
            acende_luzes_caminho_otimizado((p[0] - 1, p[1]), cont - 1)
        elif sentido == "baixo":
            if mapa[p[0] + 1][p[1]] != b'P':
                mapa[p[0] + 1][p[1]] = b'+'
            acende_luzes_caminho_otimizado((p[0] + 1, p[1]), cont - 1)
        elif sentido ==  "esquerda":
            if mapa[p[0]][p[1] - 1] != b'P': 
                mapa[p[0]][p[1] - 1] = b'+' 
            acende_luzes_caminho_otimizado((p[0], p[1] - 1), cont - 1)
        elif sentido ==  "direita":
            if mapa[p[0]][p[1] + 1] != b'P':
                mapa[p[0]][p[1] + 1] = b'+'  
            acende_luzes_caminho_otimizado((p[0], p[1] + 1), cont - 1)

# Reinicia o mapa
def reiniciar_mapa():
    global mapa
    mapa = deepcopy(mapa_original)

# Print do mapa
def print_map(matriz):
    for i in range (0, n_linhas):  
        for j in range (0, n_colunas):
            if matriz[i][j] == b'.':
                print (".", end = '')
            elif matriz[i][j] == b'0':
                print (" ", end = '')
            elif matriz[i][j] == b'P':
                print ("☺", end = '')
            elif matriz[i][j] == b'+':
                print ("+", end = '')
            else:
                print ("x", end = '')
        print() 

# Atualiza mapaint
def atualiza_mapaint(p):
    global mapaint
    mapaint[p[0], p[1]] = mapaint[p[0], p[1]] + 1 

# Ilumina mapa
def ilumina_mapa():
    global mapa
    for i in range(0, n_linhas):
        for j in range(0, n_colunas):
            if mapa[i][j] == b'P':
                p = (i, j)
                acende_luzes_em_volta(p, 4)
                acende_luzes_caminho_otimizado(p, 10)

# Rendimento em %
def calcula_rendimento():
    global mapa
    total_luzes = 0
    luzes_acesas = 0
    for i in range(0, n_linhas):
        for j in range(0, n_colunas):
            if mapa[i][j] == b'+' or mapa[i][j] == b'P':
                luzes_acesas = luzes_acesas + 1
                total_luzes = total_luzes + 1
            elif mapa[i][j] == b'0':
                total_luzes = total_luzes + 1
    return 100*(total_luzes-luzes_acesas)/total_luzes


def new_client(client, address):
    while True:
        raw_data = client.recv(size)
        if raw_data:
            # Decode the data
            data = json.loads(raw_data)
            ##print("SERVER >> Received:", data, "from", address)

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
                #prints de testes
                print("recebi do id:", data["payload"]["source"])
                print("localizacao:", data["payload"]["content"])
                # itera sobre uma lista que armazena a posicao de cada processo e atualiza todas essas funcoes:
                #atualiza_mapaint(data["payload"]["content"])
                #mapa[data["payload"]["content"][0]][data["payload"]["content"][1]] = 'P'
                #ilumina_mapa()
                #print_map(mapa)
                #print("Rendimento = ", "%.1f" % calcula_rendimento(), " % de economia")
                #reiniciar_mapa()    
                #time.sleep(0.05)
            
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
