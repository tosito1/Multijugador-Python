import socket
import pygame
import threading
import time

# Inicializar pygame
pygame.init()

# Definición de colores
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)

# Definir las dimensiones de la ventana
ANCHO_VENTANA = 800
ALTO_VENTANA = 600

# Definir la clase Jugador
class Jugador:
    def __init__(self, x, y, salud):
        self.x = x
        self.y = y
        self.salud = salud
        self.atacando = False
        self.defendiendo = False
        self.velocidad = 5
        self.movimiento = {"arriba": False, "abajo": False, "izquierda": False, "derecha": False}

    def mover(self):
        if self.movimiento["arriba"]:
            self.y -= self.velocidad
        if self.movimiento["abajo"]:
            self.y += self.velocidad
        if self.movimiento["izquierda"]:
            self.x -= self.velocidad
        if self.movimiento["derecha"]:
            self.x += self.velocidad

    def dibujar(self, pantalla):
        color = AZUL
        if self.atacando:
            color = ROJO
        elif self.defendiendo:
            color = VERDE

        # Dibuja el rectángulo que representa al jugador
        pygame.draw.rect(pantalla, color, (self.x, self.y, 50, 50))

        # Dibuja la barra de vida del jugador
        self.dibujar_barra_vida(pantalla)

    def dibujar_barra_vida(self, pantalla):
        """
        Dibuja la barra de vida del jugador en la pantalla.
        """
        barra_vida_ancho = 50
        barra_vida_alto = 5
        # Color de la barra de vida (rojo para poca vida, verde para mucha vida)
        color_vida = (255, 0, 0) if self.salud <= 20 else (0, 255, 0)

        # Dibuja la barra de vida sobre el jugador
        pygame.draw.rect(pantalla, (0, 0, 0), (self.x, self.y - 10, barra_vida_ancho, barra_vida_alto))
        pygame.draw.rect(pantalla, color_vida, (self.x, self.y - 10, (self.salud / 100) * barra_vida_ancho, barra_vida_alto))

    def atacar(self):
        self.atacando = True

    def defender(self):
        self.defendiendo = True

    def detener(self):
        self.atacando = False
        self.defendiendo = False

    def actualizar_movimiento(self, tecla, presionada):
        """
        Actualiza el estado del movimiento del jugador
        """
        if tecla == pygame.K_w:
            self.movimiento["arriba"] = presionada
        elif tecla == pygame.K_s:
            self.movimiento["abajo"] = presionada
        elif tecla == pygame.K_a:
            self.movimiento["izquierda"] = presionada
        elif tecla == pygame.K_d:
            self.movimiento["derecha"] = presionada

    def actualizar_acciones(self, tecla, presionada):
        """
        Actualiza el estado de las acciones (atacar y defender)
        """
        if tecla == pygame.K_SPACE:  # Atacar con espacio
            if presionada:
                self.atacar()
            else:
                self.detener()  # Detener ataque cuando se suelta la tecla
        elif tecla == pygame.K_LSHIFT:  # Defender con shift
            if presionada:
                self.defender()
            else:
                self.detener()  # Detener defensa cuando se suelta la tecla

# Clase Cliente
class Cliente:
    def __init__(self, host, puerto):
        self.host = host
        self.puerto = puerto
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.puerto))
        self.jugador = Jugador(400, 300, 100)
        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Juego Multijugador")
        self.clock = pygame.time.Clock()
        self.corriendo = True
        self.jugadores = {}

    def enviar_datos(self):
        while self.corriendo:
            datos = f"{self.jugador.x},{self.jugador.y},{self.jugador.salud},{int(self.jugador.atacando)},{int(self.jugador.defendiendo)}"
            self.socket.sendall(datos.encode('utf-8'))
            time.sleep(0.05)  # Envía datos a intervalos regulares

    def recibir_datos(self):
        while self.corriendo:
            try:
                datos = self.socket.recv(1024).decode('utf-8')
                if datos:
                    jugadores_data = datos.split('|')
                    self.jugadores = {}
                    for jugador_data in jugadores_data:
                        x, y, salud, atacando, defendiendo = map(int, jugador_data.split(','))
                        self.jugadores[(x, y)] = (salud, atacando, defendiendo)
            except:
                break

    def dibujar_jugadores(self):
        for (x, y), (salud, atacando, defendiendo) in self.jugadores.items():
            color = AZUL
            if atacando:
                color = ROJO
            elif defendiendo:
                color = VERDE

            pygame.draw.rect(self.ventana, color, (x, y, 50, 50))

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LSHIFT:
                    self.jugador.defender()
                elif evento.key == pygame.K_SPACE:
                    self.jugador.atacar()
                else:
                    self.jugador.actualizar_movimiento(evento.key, True)

            elif evento.type == pygame.KEYUP:
                if evento.key == pygame.K_LSHIFT or evento.key == pygame.K_SPACE:
                    self.jugador.detener()  # Detener ataque o defensa
                else:
                    self.jugador.actualizar_movimiento(evento.key, False)

    def actualizar(self):
        self.jugador.mover()  # Mover el jugador
        self.ventana.fill(BLANCO)
        self.jugador.dibujar(self.ventana)
        self.dibujar_jugadores()
        pygame.display.update()

    def ejecutar(self):
        # Hilos para recibir y enviar datos
        threading.Thread(target=self.enviar_datos, daemon=True).start()
        threading.Thread(target=self.recibir_datos, daemon=True).start()

        # Bucle principal del juego
        while self.corriendo:
            self.manejar_eventos()
            self.actualizar()
            self.clock.tick(60)  # Limita la actualización de la ventana a 60 fps para un movimiento más fluido

        pygame.quit()
        self.socket.close()

# Iniciar el cliente
if __name__ == "__main__":
    cliente = Cliente('127.0.0.1', 5555)  # Cambiar '127.0.0.1' por la IP del servidor
    cliente.ejecutar()
