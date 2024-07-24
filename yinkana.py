#!/usr/bin/env python3
import os, socket
import hashlib
import struct, sys, array, base64
import threading

#Login
def login(username: str) -> bytes:
	'''Función para acceder'''
	sock = socket.socket()
	sock.connect(('yinkana',2000))
	sock.recv(1024) #bienvenida
	sock.send(username.encode()) 

	data = receiveInstruction(sock)
	print(data.decode())
	identifier = getId(data)
	sock.close()
	
	return identifier


def getId(data: bytes) -> bytes:
	'''Función para obtener el identificador'''
	for line in data.split(b"\n"):
		if b"identifier:" in line:
			return line.split(b":")[-1]


#Reto 1: UDP
def toUpper(identifier: bytes) -> bytes: 
	'''Función del reto 1'''
	sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	port = 578
	sockUDP.bind(('', port))

	mssg = str(port) + " " + identifier.decode()
	sockUDP.sendto(mssg.encode(),('yinkana',4000))
	
	question, client = sockUDP.recvfrom(1024)
	print(question.decode())
	print(identifier.upper().decode())
	sockUDP.sendto(identifier.upper(), client)
	
	next_instruction, client = sockUDP.recvfrom(1024)
	print(next_instruction.decode())
	identifier = getId(next_instruction)
	sockUDP.close()
	
	return identifier
	
	
#Reto 2: TCP words length
def wLength(identifier: bytes) -> bytes:
	'''Función del reto 2'''
	sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockTCP.connect(('yinkana',3010))	
	counter = 0
	txt_total = b''
		
	while counter < 1000 :
		txt_parcial = sockTCP.recv(1024)
		txt_total += txt_parcial
		counter = 0
		words_length = []
		for word in txt_total.split():
			if counter<1000:
				words_length.append(str(len(word)))
				counter += len(word)
			
	msg = identifier.decode() + " " + " ".join(words_length) + " --"
	print(msg + "\n")
	sockTCP.send(msg.encode())
	
	next_instruction = receiveInstruction(sockTCP)
	identifier = getId(next_instruction)
	print(next_instruction.decode())
	sockTCP.close()
	
	return identifier


def receiveInstruction(sockTCP: socket.socket) -> bytes:	
	'''Función para obtener lo que faltaba por enviar del socket, y el siguiente enunciado'''
	next_instruction = b''
	while True: 
		remaining = sockTCP.recv(2048)
		if not remaining:
			break
		next_instruction += remaining
	return next_instruction

	
#Reto 3: TCP cakes stuff
def cakes(identifier: bytes) -> bytes:
	'''Función del reto 3'''
	sockTCP2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockTCP2.connect(('yinkana',3060))	
	sentence_length = 0
	counter = 0
	txt_total = b''
	
	while sentence_length == 0:
		txt_total += sockTCP2.recv(1024)
		sentence_length = getLength(txt_total)

	dictionary = createDictionary(txt_total, sentence_length, sockTCP2)

	cake_stuff = [dictionary[i] for i in range(1, sentence_length+1)] # Para ordenarlo	

	msg = identifier.decode() + " " + " ".join(cake_stuff) + " --"
	print(msg)
	sockTCP2.send(msg.encode())
	
	next_instruction = receiveInstruction(sockTCP2)
	print(next_instruction.decode())
	identifier = getId(next_instruction)
	sockTCP2.close()
	
	return identifier

def getLength(txt_total: bytes) -> int:
	'''Función auxiliar para obtener el número de palabras de la frase del reto 3'''
	txt_aux = txt_total.split()
						
	for word in txt_aux:
		try:
			number = int(word) # para comprobar que es el primer número sólo		
			sentence_length = number
			break 
		except: 
			continue
	return sentence_length	

def createDictionary(txt_total: bytes, sentence_length: int, sockTCP2: socket.socket) -> dict[int, str]: #orden, palabra 
	'''Función auxiliar para crear un diccionario cuyos índices sean el orden, y el contenido la palabra en sí (del reto 3)'''
	counter = 0
	while counter < sentence_length:
		txt_total += sockTCP2.recv(1024)
		counter = 0
		dictionary = {}
		txt_aux = txt_total.split()

		for word in txt_aux:
			try:
				if b':' in word:  #para evitar números solos
					index = int(word.split(b':')[1])
					if index <= sentence_length:
						valid_word = word.split(b':')[0]
						dictionary[index] = valid_word.decode()
						counter += 1
			except:
				continue
	return dictionary
	
	
#Reto 4: SHA sum
def sha(identifier: bytes) -> bytes:
	'''Función del reto 4'''
	sockTCP3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockTCP3.connect(('yinkana',9003))
	sockTCP3.send(identifier)
	
	msg = sockTCP3.recv(1024)
	file_length = int(msg.split(b":",1)[0])
	content = msg.split(b":",1)[1]

	while len(content) < file_length:
		content += sockTCP3.recv(2048)

	sha_sum = hashlib.sha1(content).digest()
	print(sha_sum)
	sockTCP3.send(sha_sum)
		
	next_instruction = receiveInstruction(sockTCP3)
	print(next_instruction.decode())
	identifier = getId(next_instruction)
	sockTCP3.close()
	
	return identifier
	
	
#Reto 5: WYP
FORMAT = "!3sBHHH" #'!' porque es para la red (big endian)
def wyp(identifier: bytes) -> bytes:
	'''Función del reto 5'''
	sockUDP1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	request = packHeader(identifier) 
	sockUDP1.sendto(request,('yinkana',6000))

	next_instruction, address = sockUDP1.recvfrom(2048)
	response = unpack(next_instruction)
	print(response.decode())
	identifier = getId(response)
	sockUDP1.close()
	
	return identifier

def packHeader(identifier: bytes) -> bytes:
	'''Función auxiliar para empaquetar (en base al formato) la cabecera del reto 5'''
	base_id = base64.b64encode(identifier)	
	header = struct.pack(FORMAT,b'WYP',0,0,0,1)
	request = header + base_id
	header = struct.pack(FORMAT,b'WYP',0,0,cksum(request),1)
	request = header+base_id
	return request

def unpack(next_instruction: bytes) -> bytes:
	'''Función auxiliar para desempaquetar la respuesta del reto 5'''
	payload_size = len(next_instruction) - 10 #10 es el tamaño de la cabecera
	response = struct.unpack(FORMAT + str(payload_size) + "s", next_instruction) # "s" es de longitud payload_size
	decoded_response = base64.b64decode(response[5]) #5 para mostrar solo el payload
	return decoded_response
	
# from scapy:
# https://github.com/secdev/scapy/blob/master/scapy/utils.py
def cksum(pkt):
    # type: (bytes) -> int
    if len(pkt) % 2 == 1:
        pkt += b'\0'
    s = sum(array.array('H', pkt))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    s = ~s

    if sys.byteorder == 'little':
        s = ((s >> 8) & 0xff) | s << 8

    return s & 0xffff


#Reto 6: web server	
def webServer(identifier: bytes) -> bytes :	
	'''Función del reto 6'''
	port = 42137
	sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Para evitar 'Address already in use'
	sockServer.bind(('', port)) 
	sockServer.listen(30)

	sockClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
	sockClient.connect(('yinkana',8002)) 
	msg = identifier.decode() + ' ' + str(port)
	sockClient.send(msg.encode())	
	sockClient.close()
	
	# Iniciar el servidor			
	client_number = 0
	try:
		while True:
			child_socket, client_address = sockServer.accept()
			client_number += 1
			thread = threading.Thread(target=handle, args=(child_socket, client_address, client_number)) 
			thread.start()
	except KeyboardInterrupt:
		sockServer.close()
		print("\n********** Web server stopped **********\n")
	
def handle(sock, client, client_number):
	'''Función para responder a los clientes con concurrencia del reto 6'''
	print(f"Client connected: {client_number} {client}")		
	# Recibir la solicitud (request) del cliente
	data = sock.recv(1024)
	print(data.decode())
	# Y separarla para obtener si es GET o POST, y la url
	request_lines = data.decode().split('\n')
	first_line = request_lines[0].strip()  
	method, path, http = first_line.split(' ') # GET | /rfc... | HTTP...
	
	if method == 'POST':
		identifier = getId(data)
		sendToFinalSocket(identifier)
		sock.close()
		print("(CTRL+C to stop the web server)")
	else:
		rfc_url = f'http://rick:81/rfc{path}'
		with socket.create_connection(('rick', 81)) as sockRFC:
			sockRFC.send(f'GET {rfc_url} HTTP/1.0\r\n\r\n'.encode())
		       	# Formato: GET <URL> HTTP/<version><additional headers>
			
			response = receiveInstruction(sockRFC)
							
			# Enviar la respuesta HTTP al cliente
			sock.send(response)
			sock.close()	

def sendToFinalSocket(identifier: bytes):
	'''Función para enviar el identificador y obtener la respuesta del último socket (reto 6)'''
	sock7 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
	sock7.connect(('yinkana',33333)) 
	sock7.send(identifier)
	congrats = receiveInstruction(sock7)
	print(congrats.decode())
	sock7.close()	
	
		
if __name__ == "__main__" :
	identifier1 = login('sharp_mendel') 
	id2 = toUpper(identifier1)
	id3 = wLength(id2)
	id4 = cakes(id3)
	id5 = sha(id4)
	id6 = wyp(id5)
	webServer(id6)
