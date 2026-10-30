import threading
import time

import datos

NUM_CAJAS = datos.NUM_CAJAS

inventario = datos.STOCK_INICIAL

pedidos = datos.PEDIDOS


def procesar_ventas():
    while True:
        if not pedidos:
            break
        p = pedidos[-1]
        if inventario[p[1]] >= p[2]:
            time.sleep(0.001)
            inventario[p[1]] -= p[2]
        del pedidos[-1]


hilos = []

for caja in range(NUM_CAJAS - 1):
    h = threading.Thread(target=procesar_ventas)
    h.start()
    hilos.append(h)

for h in hilos:
    h.join()

print("Saltan errores de varios hilos porque intentan acceder a un elemento queya  fue borrado por otro hilo")
