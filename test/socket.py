import socket
import tqdm
import os
import pickle
import database
import time
import csv
from config import SOCK

# device's IP address
SERVER_HOST = SOCK.SERVER_HOST
SERVER_PORT = SOCK.SERVER_PORT


BUFFER_SIZE = 4096  # Receive 4096 Bytes In Each Transmission
SEPARATOR = "<SEPARATOR>"


s = socket.socket() # Create The Server Socket

s.bind((SERVER_HOST, SERVER_PORT)) # Bind The Socket To Our Local Address

# --- Enabling our server to accept connections
# --- 5 here is the number of accepted connections that
# --- the system will allow before refusing new connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

# accept connection if there is any
while True:
    client_socket, address = s.accept() 
    # if below code is executed, that means the sender is connected
    print(f"[+] {address} is connected.")

    # receive the file infos
    # receive using client socket, not server socket
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)


    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    #def await_info():
    buffer = b''
    while True:
        try:
            for _ in progress:
                # read 1024 bytes from the socket (receive)
                bytes_read = client_socket.recv(BUFFER_SIZE)
                print(bytes_read)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                #f.write(bytes_read)
                buffer += bytes_read
                # update the progress bar
                progress.update(len(bytes_read))
        finally:
            output = pickle.loads(buffer)
            print('output', output)
            database.writeToDatabase(output)
            break

        # close the client socket
        client_socket.close()
        # close the server socket
        s.close()