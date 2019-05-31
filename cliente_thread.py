import pickle
import socket
import zlib
import time

def main():
    #host = "10.10.150.14"
    HOST = "10.10.150.14"
    PORT = 9999
    print("Intentando conectar a %s" % HOST)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        inicio = time.time()
        s.sendall(b"dame lista")

        data = s.recv(2048)
        data = pickle.loads(data)
        duracion = time.time() - inicio
    print('Received',repr(data))
    print("tiempo de ejecución: %f" % duracion)


if __name__ == "__main__":
    main()

