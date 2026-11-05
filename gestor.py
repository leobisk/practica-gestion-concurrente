import threading
import time
from random import randint

import datos


class GestorInventario:
    def __init__(self, stock_inicial, reposiciones):
        self.inventario = stock_inicial
        self.reposiciones = reposiciones
        self.lock = threading.RLock()
        self.condicion = threading.Condition(
            self.lock
        )  # La condicion recibe el lock para que cuando un hilo la esté esperando
        # pueda liberarlo permitiendo que el resto de cajas continuen mientras esta espera

    def hay_stock(self, prod, cant) -> bool:
        with self.lock:
            return self.inventario[prod] >= cant

    def descontar(self, prod, cant):
        with self.lock:
            self.inventario[prod] -= cant

    # Operacion con lock que llama a hay_stock() que tambien esta protegida y
    # mientras hay_stock devuelve True llama a descontar() que tambien está protegida
    def vender(self, prod, cant):
        with self.lock:
            time.sleep(0.1)
            if self.hay_stock(prod, cant):
                self.descontar(prod, cant)
            else:
                print(f"Sin stock de {prod}, esperando reposición")
                self.condicion.wait()
                if self.hay_stock(prod, cant):
                    self.descontar(prod, cant)

    def reponer(self):
        time.sleep(4)
        with self.lock:
            for _, prod, cant in self.reposiciones:
                self.inventario[prod] += cant
            self.condicion.notify_all()


gestor = GestorInventario(datos.STOCK_INICIAL, datos.REPOSICIONES)
pedidos = datos.PEDIDOS
lock_pedidos = threading.Lock()
semaforo = threading.Semaphore(datos.NUM_TERMINALES)
barrera = threading.Barrier(datos.NUM_REVISORES)
resumen = {}


def caja():
    while True:
        with lock_pedidos:
            if not pedidos:
                return
            _, prod, cant = pedidos.pop()
        with semaforo:
            gestor.vender(prod, cant)


def revisor(i, productos):
    for p in productos[0:len(productos) // 2]:
        resumen[p] = gestor.inventario[p]
    time.sleep(randint(1, 4))
    print(f"Revisor {i}: fase 1 completada")
    barrera.wait()
    print(f"Revisor {i}: fase 2")
    for p in productos[len(productos) // 2:]:
        resumen[p] = gestor.inventario[p]
    time.sleep(1)


if __name__ == "__main__":
    print("Iniciando Ejecucion...\n")
    threading.Thread(target=gestor.reponer).start()

    cajas = [threading.Thread(target=caja) for _ in range(datos.NUM_CAJAS)]
    for h in cajas:
        h.start()
    for h in cajas:
        h.join()
    print("\nPedidos pendientes completados, iniciando revisión...\n")
    productos = list(gestor.inventario)
    revisores = [threading.Thread(target=revisor, args=(i, productos[i::datos.NUM_REVISORES])) for i in range(datos.NUM_REVISORES)]
    for r in revisores:
        r.start()
    for r in revisores:
        r.join()

    print("\nInventario final:\n")
    for prod, stock in resumen.items():
        print(f"{prod:<25} {stock}")
