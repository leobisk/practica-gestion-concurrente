import threading
import time
from random import randint

import datos


class GestorInventario:
    def __init__(self, stock_inicial, reposiciones):
        self.inventario = stock_inicial
        self.reposiciones = reposiciones
        self.repuesto = False
        self.lock = threading.RLock()
        hilos = []
        self.cancelados = []
        self.resultados = {}
        self.rechazadas = []
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
    def vender(self, prod, cant, ped):
        with self.lock:
            if ped in self.cancelados:
                self.resultados[ped] = "cancelado"
                return
            time.sleep(datos.TIEMPO_COBRO)
            if ped in self.cancelados:
                self.resultados[ped] = "cancelado"
                return
            if self.hay_stock(prod, cant):
                self.descontar(prod, cant)
                self.resultados[ped] = "completado"
            else:
                print(f"Sin stock de {prod}, esperando reposición")
                while not self.hay_stock(prod, cant) and not self.repuesto:
                    self.condicion.wait()
                    if ped in self.cancelados:
                        self.resultados[ped] = "cancelado"
                        return
                    if self.hay_stock(prod, cant):
                        self.descontar(prod, cant)
                        self.resultados[ped] = "completado"


    def reponer(self):
        for _, prod, cant in self.reposiciones:
            time.sleep(2)
            with self.lock:
                self.inventario[prod] += cant
                self.condicion.notify_all()

    def cancelador(self,cancelaciones,pedidos):
        hilos = []
        def cancelar(pedido, tiempo):
            time.sleep(tiempo)
            self.cancelados.append(pedido)
        for _, pedido, tiempo in cancelaciones:
            h = threading.Thread(target=cancelar, args=(pedido,tiempo))
            h.start()
            hilos.append(h)

def caja():
    while True:
        with lock_pedidos:
            if not pedidos:
                return
            ped, prod, cant = pedidos.pop()
        with semaforo:
            gestor.vender(prod, cant, ped)


def revisor(i, productos):
    for p in productos[0 : len(productos) // 2]:
        resumen[p] = gestor.inventario[p]
    time.sleep(randint(1, 4))
    print(f"Revisor {i}: fase 1 completada")
    barrera.wait()
    print(f"Revisor {i}: fase 2")
    for p in productos[len(productos) // 2 :]:
        resumen[p] = gestor.inventario[p]
    time.sleep(1)



if __name__ == "__main__":
    print("Iniciando Ejecucion...\n")
    gestor = GestorInventario(datos.STOCK_INICIAL, datos.REPOSICIONES)
    pedidos = datos.PEDIDOS
    lock_pedidos = threading.Lock()
    semaforo = threading.Semaphore(datos.NUM_TERMINALES)
    barrera = threading.Barrier(datos.NUM_REVISORES)
    resumen = {}
    threading.Thread(target=gestor.reponer).start()

    cajas = [threading.Thread(target=caja) for _ in range(datos.NUM_CAJAS)]
    for h in cajas:
        h.start()
    gestor.cancelador(datos.CANCELACIONES)
    for h in cajas:
        h.join()
    print("\nPedidos pendientes completados, iniciando revisión...\n")
    productos = list(gestor.inventario)
    revisores = [
        threading.Thread(target=revisor, args=(i, productos[i :: datos.NUM_REVISORES]))
        for i in range(datos.NUM_REVISORES)
    ]
    for r in revisores:
        r.start()
    for r in revisores:
        r.join()

    print("\nInventario final:\n")
    for prod, stock in resumen.items():
        print(f"{prod:<25} {stock}")
    print(gestor.resultados)
