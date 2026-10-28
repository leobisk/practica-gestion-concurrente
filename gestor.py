import threading

import datos

import time
NUM_CAJAS = datos.NUM_CAJAS

inventario = datos.STOCK_INICIAL

pedidos = datos.PEDIDOS

def procesar_ventas():
    while pedidos:
        p = pedidos[-1]
        time.sleep(0.001)
        if inventario[p[1]] >= p[2]:
            time.sleep(0.001)
            inventario[p[1]] -= p[2]
        del pedidos[-1]

hilos = []
print(sum([prod for prod in inventario.values()]))
for caja in range(NUM_CAJAS -1):
    h = threading.Thread(target=procesar_ventas)
    h.start()
    hilos.append(h)

for h in hilos:
    h.join()

print(sum([prod for prod in inventario.values()]))
