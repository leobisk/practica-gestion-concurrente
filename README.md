## Preguntas de reflexion

### Fase 1, parte critica del race condition

La parte crítica ocurre cuando se lee el estado del inventario y se hacen las operacion de comprobacion hasta eliminar el pedido, otro hilo podria estar procesando el mismo pedido al mismo tiempo.
