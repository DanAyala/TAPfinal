import multiprocessing
from urllib.parse import urlparse
import hashlib
from cryptography.fernet import Fernet
import base64
import concurrent.futures
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pickle
import socket
import zlib
import time


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

def es_el_password(libro, lista_passwords, firma_hash):

    archivo = os.path.splitext(libro)
    texto_encriptado = lee_archivo_pickle(archivo[0] + '.pkl')
    for pwd in lista_passwords:
        llave = obten_llave(pwd)
        texto_desencriptado = desencripta(texto_encriptado,llave)
        hash_desencriptado  = encrypt_string(texto_desencriptado)
        if (hash_desencriptado == firma_hash) == True:
            return libro, pwd


def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string).hexdigest()
    return sha_signature


def lee_archivo_diccionario(nombre_archivo):
    with open(nombre_archivo,"rb") as fh:
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
    with open(archivo,"r") as fh:
        lista = fh.readlines()
    for l in lista:
        url_parts = urlparse(l)
        archivo = os.path.basename(url_parts.path)
        lista_urls.append(archivo.strip("\n"))
    return lista_urls

def busca_passwords(lista_libros,lista_passwords,diccionario_hash):
    futures = []
    diccionario = []
    hilos = multiprocessing.cpu_count()
    #print(lista_libros)
    #for x in range(hilos):
    for libro in lista_libros:
        archivo = os.path.splitext(libro)
        texto_enc = lee_archivo_pickle(archivo[0]+'.pkl')
        hash_texto_original = diccionario_hash[libro]

        pool = concurrent.futures.ThreadPoolExecutor(max_workers=hilos)


        futures.append(pool.submit(es_el_password,libro, lista_passwords, hash_texto_original))

    for x in concurrent.futures.as_completed(futures):
        print(x.result())
        diccionario.append(x.result())
    return diccionario


def main():
    HOST = "10.10.162.114"
    PORT = 9999
    print("Intentando conectar a %s" % HOST)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))

        while True:
            valor = input("ingresa un numero de libros para procesar en el cliente: ")

            v = pickle.dumps(valor)
            s.sendall(v)
            listaCliente = list()
            inicio = time.time()
            archivo_passwords = '10-million-password-list-top-1000000.txt'
            texto_passwords   = lee_archivo(archivo_passwords)
            lista_passwords   = haz_lista_palabras(texto_passwords)
            #diccionario de hashes
            dhash = lee_archivo_diccionario("diccionario_hashs.pkl")
            #lista de libros a procesar
            libros = "urls_libros.txt"
            lista_libros = carga_lista_archivos(libros)

            contador = 0
            #Se divide las lista de los libros para cliente y servidor
            l = 30
            for libros in lista_libros:
                if contador < l:
                    listaCliente.append(libros)

                contador +=1

            lista = busca_passwords(listaCliente,lista_passwords,dhash)
            print("Total de libros procesados por el cliente: ", len(listaCliente))
            data = s.recv(2048)
            s.sendall(b"stop")
            s.close()
            listaServidor = pickle.loads(data)

            for i in listaServidor:
                listaCliente.append(i)
            print(len(listaCliente))
            print(listaCliente)

            duracion = time.time() - inicio
            print("tiempo de ejecucion: %f" % duracion)
            break
            # pwd = '123456789'
            # texto_enc = lee_archivo_pickle('pg51804.pkl')
            # d = lee_archivo_diccionario("diccionario_hashs.pkl")
            # hash_texto_original = d['pg51804.txt']
            # print(es_el_password(texto_enc, pwd, hash_texto_original))



if __name__ == "__main__":
    main()