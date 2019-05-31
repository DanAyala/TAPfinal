from urllib.parse import urlparse
import pickle
import hashlib
import time
from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import concurrent.futures
import socket
import sys
import multiprocessing

diccionario_libro_pwd = {}


def main():
    HOST = "10.10.150.14"
    PORT = 9999
    print("Intentando conectar a %s" % HOST)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            message = s.recv(2048)
            if message == b'start':
                workers = multiprocessing.cpu_count()
                bottom = int.from_bytes(s.recv(2048), "big")
                len = int.from_bytes(s.recv(2048), "big")
                print(f'Workers: {workers}')
                print(f'Nucleos: {multiprocessing.cpu_count()}')
                print(f'Lote de procesamiento {bottom + 1} al {len}\n')
                hashing(workers, bottom, s)
                break
            print(message.decode())
            mensaje = input("Mensaje: ").encode("UTF-8")
            if not mensaje:
                s.sendall(b'0')
            if mensaje == b'bye':
                s.sendall(b'stop')
                sys.exit(0)
            s.sendall(mensaje)


def lee_archivo(nombre_archivo):
    try:
        texto = ""
        with open(nombre_archivo, "r") as archivo:
            texto = archivo.read()
        return texto
    except IOError as ioe:
        print(ioe.strerror)
        return None


def lee_archivo_pickle(nombre_archivo):
    try:
        texto = ""
        with open(nombre_archivo, "rb") as archivo:
            texto = pickle.load(archivo)
        return texto
    except IOError as ioe:
        print(ioe.strerror)
        return None


def desencripta(encriptado, key):
    f = Fernet(key)
    try:
        texto_original = f.decrypt(encriptado)
        return texto_original
    except:
        return b""


def obten_llave(password_provided):
    password = password_provided.encode()  # Convert to type bytes
    salt = b'salt_'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def es_el_password(texto_encriptado, password, firma_hash):
    llave = obten_llave(password)
    texto_desencriptado = desencripta(texto_encriptado, llave)
    hash_desencriptado = encrypt_string(texto_desencriptado)
    return hash_desencriptado == firma_hash


def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string).hexdigest()
    return sha_signature


def lee_archivo_diccionario(nombre_archivo):
    with open(nombre_archivo, "rb") as fh:
        diccionario = pickle.load(fh)
    return diccionario


def haz_lista_palabras(texto):
    try:
        lista_palabras = texto.split()
        lista = []
        for palabra in lista_palabras:
            palabra = palabra.strip(".")
            palabra = palabra.strip(",")
            lista.append(palabra)
        return lista
    except:
        return None


def carga_lista_archivos(archivo):
    lista_urls = list()
    with open(archivo, "r") as fh:
        lista = fh.readlines()
    for l in lista:
        url_parts = urlparse(l)
        archivo = os.path.basename(url_parts.path)
        lista_urls.append(archivo.strip("\n"))
    return lista_urls


def busca_passwords(libro, lista_passwords, diccionario_hash):
    archivo = os.path.splitext(libro)
    texto_enc = lee_archivo_pickle(archivo[0] + '.pkl')
    hash_texto_original = diccionario_hash[libro]
    for pwd in lista_passwords:
        if es_el_password(texto_enc, pwd, hash_texto_original):
            # print(libro,pwd)
            diccionario_libro_pwd[libro] = pwd
            break


def hashing(numworkers, bottom, server):
    inicio = time.time()
    # lista de paswords
    path = './'
    archivo_passwords = path + '10-million-password-list-top-1000000.txt'
    texto_passwords = lee_archivo(archivo_passwords)
    lista_passwords = haz_lista_palabras(texto_passwords)
    # diccionario de hashes
    dhash = lee_archivo_diccionario("diccionario_hashs.pkl")
    # lista de libros a procesar
    libros = "urls_libros.txt"
    lista_libros = carga_lista_archivos(libros)
    # numworkers=(int)(input("Introduzca nÃºmero de trabajadores"))
    hilos = []
    with concurrent.futures.ThreadPoolExecutor(numworkers) as executor:
        for l in lista_libros[bottom::]:
            e = executor.submit(busca_passwords, l, lista_passwords, dhash)
            hilos.append(e)

    serv_dic = pickle.loads(server.recv(2048))
    diccionario = {**serv_dic, **diccionario_libro_pwd}
    print(diccionario)
    duracion = time.time() - inicio
    print("\nHecho. Tiempo de ejecucion: %f" % duracion)


if __name__ == "__main__":
    main()