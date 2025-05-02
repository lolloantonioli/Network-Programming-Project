import socket
import os
import mimetypes
from datetime import datetime # Per stampare l'ora nei log

HOST = 'localhost'  # Il server ascolta solo su localhost
PORT = 8080         # Porta su cui ascolta il server
DIRECTORY = 'www'   # Cartella dove sono i file

# Funzione che stampa le informazioni del logging delle richieste
def log_request(method, path, status_code):
    print(f"[{datetime.now()}] {method} {path} -> {status_code}")

# Funzione che genera la risposta HTTP
def generate_response(path):
    full_path = os.path.join(DIRECTORY, path.lstrip('/')) # Rimuove "/" iniziale e costruisce il path completo

    # Se è una cartella, prova a servire index.html
    if os.path.isdir(full_path):
        full_path = os.path.join(full_path, 'index.html')

    if os.path.exists(full_path) and not os.path.isdir(full_path):
        # File esistente → restituisce 200 OK
        with open(full_path, 'rb') as f:
            content = f.read()
        mime_type, _ = mimetypes.guess_type(full_path) # Determina il tipo di file
        return b"HTTP/1.1 200 OK\r\n" + \
               f"Content-Type: {mime_type or 'application/octet-stream'}\r\n\r\n".encode() + \
               content, 200
    else:
        # File non trovato → 404 Not Found
        content = b"<h1>404 Not Found</h1>"
        return b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n" + content, 404

def start_server():
    # Crea un socket TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT)) # Assegna IP e porta
    server.listen(1)
    print(f"Web Server is up on http://{HOST}:{PORT}")

    try:
        while True:
            client, address = server.accept()           # Attende una nuova connessione
            with client:
                request = client.recv(1024).decode()    # Riceve la richiesta HTTP
                if not request:
                    continue
                request_line = request.splitlines()[0]  # Prende solo la prima riga
                method, path, _ = request_line.split()  # Estrae metodo (GET), percorso, protocollo
                
                if method == 'GET':
                    response, status = generate_response(path)  # Genera risposta
                    log_request(method, path, status)           # Stampa log
                    client.sendall(response)                    # Invia la risposta al browser
                else:
                    # Metodo non supportato (es: POST)
                    response = b"HTTP/1.1 405 Method Not Allowed\r\n\r\n"
                    client.sendall(response)
                    log_request(method, path, 405)

    except KeyboardInterrupt:
        print('\n[!] CTRL+C revealed. Server closing...')
    finally:
        server.close()
        print('[*] Server correctly closed')

if __name__ == "__main__":
    start_server()
