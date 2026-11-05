# PRÁCTICA UD2 · StockFlow

## Descripción general del proyecto.

Un script de python que usa varios hilos concurrentes para simular las ventas de una lista de pedidos, usando RLocks, barreras, semaforos y condiciones

## Comandos para ejecutar la actividad:

    git clone https://github.com/leobisk/practica-gestion-concurrente && cd practica-gestion-concurrente
    python gestor.py

## Estructura de archivos

```
    practica-gestion-concurrente/
        ├── datos.py
        ├── gestor.py
```

## Explicación de la condición de carrera inicial

La parte crítica ocurre mientras se lee el estado del inventario, se hacen las operacion de comprobacion hasta eliminar el pedido, otro hilo podria estar procesando el mismo pedido al mismo tiempo, o se podria intentar leer un pedido que ya no existe lanzando una excepción (usando la version inicial de feature/race-condition).


## Uso y finalidad de Lock, RLock, Semaphore, Condition y Barrier

### Lock / Rlock

Usado durante la lectura, escritura y comprobacion de datos para evitar colisiones en las operaciones concurrentes, usando rlock en la version final para habilitar la reentrada al usar distintas funciones

### Semaphore

Usado para simular un numero de cajas concurrentes , limitando la cantidad de hilos que estan activos al mismo tiempo

### Condition

Usado para liberar el lock cuando no se cumple una condicion y congelar el hilo hasta que se cumpla esta

### Barrier

Usado para congelar un hilo hasta que un determinado numero de hilos estén en las mismas condiciones

## Posible deadlock y formas de evitarlo

Un deadlock podria ocurrir si una caja entra en espera despues de que se realize el restock (que solo ocurre una vez), esta se quedaria esperando indefinidamente

Solucion:

A: Usar wait con timeout

B: Ejecutar restock cada cierto tiempo para volver a notificar a los hilos
