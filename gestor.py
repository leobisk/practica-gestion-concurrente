import threading
import time

import datos

NUM_CAJAS = datos.NUM_CAJAS

NUM_TERMINALES = datos.NUM_TERMINALES

inventario = datos.STOCK_INICIAL

pedidos = datos.PEDIDOS

lock = threading.Lock()

semaforo = threading.Semaphore(NUM_TERMINALES)

terminales_activos = 0
max_activos = 0

def procesar_ventas():
    global terminales_activos, max_activos
    while True:
        with semaforo:  # Dentro del bucle para que este sea concurrente pero las operaciones estan limitadas por el semaforo
            print("Terminal adquirido por semaforo")
            terminales_activos += 1
            max_activos = max(max_activos,terminales_activos)
            with lock:
                if not pedidos:
                    terminales_activos -= 1
                    break
                p = pedidos[-1]
                if inventario[p[1]] >= p[2]:
                    time.sleep(0.001)
                    inventario[p[1]] -= p[2]
                del pedidos[-1]
                print("Terminal liberado por semaforo")
                terminales_activos -= 1


hilos = []

for caja in range(NUM_CAJAS - 1):
    h = threading.Thread(target=procesar_ventas)
    h.start()
    hilos.append(h)

for h in hilos:
    h.join()

print(f"Numero maximo de terminales activos al mismo tiempo: {max_activos}")
