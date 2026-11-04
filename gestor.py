from random import randint
import threading
import time

import datos

NUM_CAJAS = datos.NUM_CAJAS

NUM_TERMINALES = datos.NUM_TERMINALES

REVISORES = datos.NUM_REVISORES

reposiciones = datos.REPOSICIONES

inventario = datos.STOCK_INICIAL

pedidos = datos.PEDIDOS

lock = threading.Lock()

semaforo = threading.Semaphore(NUM_TERMINALES)

condicion = threading.Condition()

barrera = threading.Barrier(REVISORES)

def procesar_ventas():
    while True:
        with semaforo:  # Dentro del bucle para que este sea concurrente pero las operaciones estan limitadas por el semaforo
            with lock:
                if not pedidos:
                    break
                p = pedidos[-1]
                if inventario[p[1]] >= p[2]:
                    inventario[p[1]] -= p[2]
                else:
                    with condicion:
                        print("Sin stock, esperando reposicion")
                        condicion.wait()
                        if inventario[p[1]] >= p[2]:
                            inventario[p[1]] -= p[2]
                            print("Venta realizada con exito")
                        else:
                            print("Sigue faltando stock")
                del pedidos[-1]

def reponedor():
    time.sleep(3)
    with condicion:
        for _, prod, stock in reposiciones:
            inventario[prod] += stock
        condicion.notify_all()  # Usa all porque solo se repone una vez y puede haber mas de un hilo esperando
    print("Inventario repuesto")

def revisor():
    time.sleep(randint(1,4)) # Simula revisar algo con duracion desconocida
    print("1ª fase de la revision completada, esperando al resto de revisores...")
    barrera.wait()
    print("Empezando 2ª fase")
    time.sleep(1)


hilos = []

threading.Thread(target=reponedor).start()

for caja in range(NUM_CAJAS - 1):
    h = threading.Thread(target=procesar_ventas)
    h.start()
    hilos.append(h)

for h in hilos:
    h.join()

revisores = []

for _ in range(REVISORES):
    h = threading.Thread(target=revisor)
    h.start()
    revisores.append(h)

for r in revisores:
    r.join()
