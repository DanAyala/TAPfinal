#!/usr/bin/env python3
import concurrent.futures
import multiprocessing
import time


def primos(inicio, fin):
  numeros_primos = list()
  for num in range(inicio,fin + 1):
    if (num > 1):
      for i in range(2,num):
        if (num % i) == 0:
          break
      else:
          #print(num)
          numeros_primos.append(num)
  return numeros_primos


def main(numero, hilos):
    #threads = []
    rango = int( numero / hilos )
    start = 0
    end = 0
    futures = []
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=hilos)
    for x in range(hilos):
        end = (start + rango - 1)
        futures.append(pool.submit(primos, start, end))
        start = start + rango
    for x in concurrent.futures.as_completed(futures):
        print(x.result())

def procesa(inicio, final, hilos):
    numero = final - inicio
    rango = int( numero / hilos )
    start = 0
    end = 0
    futures = []
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=hilos)
    for x in range(hilos):
        end = (start + rango - 1)
        futures.append(pool.submit(primos, start, end))
        start = start + rango
    primes_sum = 0
    for x in concurrent.futures.as_completed(futures):
        print("abajo va algo")
        print(x.result())
        primes_sum = primes_sum + len( x.result)
    print("numeros primos entre %d y %d : %d" % (inicio,final,primes_sum))


if __name__ == "__main__":
    start_time = time.time()
    cores = multiprocessing.cpu_count()
    #main(20,cores)
    procesa(0,100000,cores+4)
    duration = time.time() - start_time
    print("Tiempo en segundos:%f" % duration)

#[17, 19]
#[2, 3]
#[5, 7]
#[11, 13]