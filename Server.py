#!/usr/bin/env python3
import hashlib
import json
import time
import pickle
import socket
from urllib.parse import urlparse
from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

HOST = '10.10.153.172'  #  (localhost)
PORT = 9999        # Port

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
    texto_desencriptado = desencripta(texto_encriptado,llave)
    hash_desencriptado  = hash_string(texto_desencriptado)
    return hash_desencriptado == firma_hash

def hash_string(cadena):
    sha_signature = \
        hashlib.sha256(cadena).hexdigest()
    return sha_signature


def lee_archivo_diccionario(nombre_archivo):
    with open(nombre_archivo,"rb") as fh:
        diccionario = pickle.load(fh)
    return diccionario
#todo Poder encontrar la manera de insertar los threads

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
    lista_encontrados =  list()
    for libro in lista_libros:
        archivo = os.path.splitext(libro)
        texto_enc = lee_archivo_pickle(archivo[0]+'.pkl')
        hash_texto_original = diccionario_hash[libro]
        for pwd in lista_passwords:
            if es_el_password(texto_enc, pwd, hash_texto_original):
                print(libro,pwd)
                lista_encontrados.append([libro,pwd])
#
                break
    return lista_encontrados


def main(host, port):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    c.bind((host, port))
    c.listen(50)
    print("Esperando conexion en puerto %d" % port)
    while True:
        current, adress = c.accept()


        while True:
            data = current.recv(2048)
            if (data == b"stop"):
                current.shutdown(1)
                current.close()
                exit()
            elif data:
                print("Leyendo passwords")
                archivo_passwords = '10-million-password-list-top-1000000.txt'
                texto_passwords = lee_archivo(archivo_passwords)
                lista_passwords = haz_lista_palabras(texto_passwords)
                # diccionario de hashes
                print("Leyendo hashes")
                dhash = lee_archivo_diccionario("diccionario_hashs.pkl")
                # lista de libros a procesar
                print("Leyendo lista libros")
                libros = "urls_libros.txt"
                lista_libros = carga_lista_archivos(libros)
                print("Buscando passwords")
                lista = busca_passwords(lista_libros, lista_passwords, dhash)
                print(lista)
                l=pickle.dumps(lista)
                current.sendall(l)


if __name__ == "__main__":
    inicio = time.time()
    main(HOST, PORT)
    duracion = time.time() - inicio