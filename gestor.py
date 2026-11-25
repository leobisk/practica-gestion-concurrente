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
        self.evento = threading.Event()
        self.evento.set()
        self.pausa_realizada = False
        self.requests = []
        self.lock_requests = threading.Lock()
        self.lock_reposiciones = threading.Lock()
        self.resumen = {}
        self.historial_reposiciones = []

    def hay_stock(self, prod, cant) -> bool:
        with self.lock:
            return self.inventario[prod] >= cant

    def ver_stock(self, prod):
        with self.lock:
            return self.inventario[prod]

    def descontar(self, prod, cant):
        with self.lock:
            self.inventario[prod] -= cant

    # Operacion con lock que llama a hay_stock() que tambien esta protegida y
    # mientras hay_stock devuelve True llama a descontar() que tambien está protegida
    def vender(self, prod, cant, num_caja, ped):
        nombre_caja = "Caja " + str(num_caja)
        self.resumen.setdefault(nombre_caja, {"antes": [], "durante": [], "despues": []})
        esperando = False
        with self.lock:
            time.sleep(0.1)
            if self.hay_stock(prod, cant):
                self.descontar(prod, cant)
            else:
                print(f"Sin stock de {prod}, esperando reposición")
                esperando = True
        if esperando:
            evento = threading.Event()
            self.requests.append((evento, prod))
            evento.wait()
            with self.lock:
                if self.hay_stock(prod, cant):
                    self.descontar(prod, cant)
            if not self.evento.is_set():
                self.resumen[nombre_caja]["durante"].append(ped)
            else:
                if self.pausa_realizada:
                    self.resumen[nombre_caja]["despues"].append(ped)
                else:
                    self.resumen[nombre_caja]["antes"].append(ped)


    def reponedor(self, num_almacen):
        almacen = "Almacen " + str(num_almacen)
        while True:
            time.sleep(0.1)
            if not pedidos: return

            with self.lock_requests:
                verificado = False
                if self.requests:
                    verificado = True
                    evento, prod = self.requests.pop()

            if verificado:
                verificado = False
                with self.lock_reposiciones:
                    for indx, repo in enumerate(self.reposiciones):
                        if repo[1] == prod:
                            alb,  _, cant = self.reposiciones.pop(indx)
                            verificado = True

            if verificado:
                with self.lock:
                    self.inventario[prod] += cant
                evento.set()
                self.historial_reposiciones.append((alb, prod, cant, almacen))


    # def reponer(self):
    #     time.sleep(4)
    #     with self.lock:
    #         for _, prod, cant in self.reposiciones:
    #             self.inventario[prod] += cant
    #         self.condicion.notify_all()


gestor = GestorInventario(datos.STOCK_INICIAL, datos.REPOSICIONES)
pedidos = datos.PEDIDOS
lock_pedidos = threading.Lock()
semaforo = threading.Semaphore(datos.NUM_TERMINALES)
barrera = threading.Barrier(datos.NUM_REVISORES)
resumen = {}


def espera():
    time.sleep(3)
    print("Pausa iniciada")
    print(len(pedidos), " Pedidos Restantes")
    gestor.evento.clear()

    time.sleep(4)

    gestor.evento.set()
    gestor.pausa_realizada = True
    print("Pausa quitada")
    print(len(pedidos), " Pedidos Restantes")


def caja(num_caja):
    while True:
        time.sleep(0.3)
        if gestor.evento.is_set():
            with lock_pedidos:
                if not pedidos:
                    return
                ped, prod, cant = pedidos.pop()
            with semaforo:
                gestor.vender(prod, cant, num_caja, ped)
        else:
            gestor.evento.wait()


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
    # threading.Thread(target=gestor.reponer).start()

    cajas = [threading.Thread(target=caja, args=(_,)) for _ in range(datos.NUM_CAJAS)]
    almacenes = [threading.Thread(target=gestor.reponedor, args=(_,)) for _ in range(1,3)]
    threading.Thread(target=espera).start()
    for h in almacenes:
        h.start()

    for h in cajas:
        h.start()
    for h in cajas:
        h.join()

    # print("\nPedidos pendientes completados, iniciando revisión...\n")
    # productos = list(gestor.inventario)
    # revisores = [threading.Thread(target=revisor, args=(i, productos[i::datos.NUM_REVISORES])) for i in range(datos.NUM_REVISORES)]
    # for r in revisores:
    #     r.start()
    # for r in revisores:
    #     r.join()

    # print("\nInventario final:\n")
    # for prod, stock in resumen.items():
    #     print(f"{prod:<25} {stock}")
#
#     for caja in gestor.resumen:
#         print(caja,": ")
#         print("     Antes de la pausa: ")
#         print("         ",*gestor.resumen[caja]["antes"])
#         print("     Durante de la pausa: ")
#         print("         ",*gestor.resumen[caja]["durante"])
#         print("     Despues de la pausa: ")
#         print("         ",*gestor.resumen[caja]["despues"])

    print("\nResumen reposiciones")
    for alb, prod, cant, almacen in gestor.historial_reposiciones:
        print(f"{alb} | {prod} | +{cant} | {almacen}")
