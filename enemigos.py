class Enemigo:
    def __init__(self, x, y, salud, velocidad):
        self.x = x
        self.y = y
        self.salud = salud
        self.velocidad = velocidad

    def mover_hacia(self, jugador_x, jugador_y):
        # Movimiento hacia el jugador más cercano
        if self.x < jugador_x:
            self.x += self.velocidad
        elif self.x > jugador_x:
            self.x -= self.velocidad

        if self.y < jugador_y:
            self.y += self.velocidad
        elif self.y > jugador_y:
            self.y -= self.velocidad

    def atacar(self, jugador):
        # Verificar si el enemigo está lo suficientemente cerca del jugador
        distancia = ((self.x - jugador['x']) ** 2 + (self.y - jugador['y']) ** 2) ** 0.5
        if distancia < 50:  # Rango de ataque (50 píxeles)
            jugador['salud'] -= 10  # Reduce la salud del jugador
            jugador['salud'] = max(jugador['salud'], 0)  # Asegurarse de que la salud no sea negativa
