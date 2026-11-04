import threading
import time

import datos

NUM_CAJAS = datos.NUM_CAJAS

NUM_TERMINALES = datos.NUM_TERMINALES

reposiciones = datos.REPOSICIONES

inventario = datos.STOCK_INICIAL

pedidos = datos.PEDIDOS

lock = threading.Lock()

semaforo = threading.Semaphore(NUM_TERMINALES)

condicion = threading.Condition()


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

hilos = []

threading.Thread(target=reponedor).start()

for caja in range(NUM_CAJAS - 1):
    h = threading.Thread(target=procesar_ventas)
    h.start()
    hilos.append(h)

for h in hilos:
    h.join()
