import multiprocessing
from urllib.parse import urlparse
import concurrent.futures
import pickle
import hashlib
import concurrent.futures
import multiprocessing
import time
from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


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

def es_el_password(libro,texto_encriptado, password, firma_hash):
    llave = obten_llave(password)
    texto_desencriptado = desencripta(texto_encriptado,llave)
    hash_desencriptado  = encrypt_string(texto_desencriptado)
    if (hash_desencriptado == firma_hash) == True:
        return libro,password


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

#--------------------------------------------------------------------------------
#aqui es
def busca_passwords(lista_libros,lista_passwords,diccionario_hash, path):
    for libro in lista_libros:
        archivo = os.path.splitext(libro)
        texto_enc = lee_archivo_pickle(path + archivo[0]+'.pkl')
        hash_texto_original = diccionario_hash[libro]
        for pwd in lista_passwords:
            es_el_password(libro,texto_enc, pwd, hash_texto_original)
            print(libro,pwd)
            break
#------------------------------------------------------------------------------


def main():
    inicio = time.time()
    #lista de paswords
    path = 'C:/Users/bryan/Desktop/tap_proyecto/'
    archivo_passwords = path + '10-million-password-list-top-1000000.txt'
    texto_passwords   = lee_archivo(archivo_passwords)
    lista_passwords   = haz_lista_palabras(texto_passwords)
    #diccionario de hashes
    dhash = lee_archivo_diccionario(path + "diccionario_hashs.pkl")
    #lista de libros a procesar
    libros = path + "urls_libros_short.txt"
    lista_libros = carga_lista_archivos(libros)





    busca_passwords(lista_libros,lista_passwords,dhash, path)



    #texto_enc = lee_archivo_pickle('pg51804.pkl')
    # hash_texto_original = d['pg51804.txt']
    # for pwd in lista_passwords:
    #     if es_el_password(texto_enc, pwd, hash_texto_original):
    #         print(pwd)
    #         break

    duracion = time.time() - inicio
    print("tiempo de ejecucion: %f" % duracion)
    # pwd = '123456789'
    # texto_enc = lee_archivo_pickle('pg51804.pkl')
    # d = lee_archivo_diccionario("diccionario_hashs.pkl")
    # hash_texto_original = d['pg51804.txt']
    # print(es_el_password(texto_enc, pwd, hash_texto_original))



if __name__ == "__main__":
    main()

