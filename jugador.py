class Jugador:
    def __init__(self, x, y, salud):
        self.x = x
        self.y = y
        self.salud = salud
        self.atacando = False
        self.defendiendo = False

    def atacar(self):
        self.atacando = True

    def defender(self):
        self.defendiendo = True

    def detener_accion(self):
        self.atacando = False
        self.defendiendo = False

    def actualizar(self):
        return {
            "x": self.x,
            "y": self.y,
            "salud": self.salud,
            "atacando": self.atacando,
            "defendiendo": self.defendiendo
        }
