import socket
import pygame
import threading
import time
import random

# Inicializar pygame
pygame.init()

# Definición de colores
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
NEGRO = (0, 0, 0)

# Dimensiones de la ventana
ANCHO_VENTANA = 800
ALTO_VENTANA = 600

# Definir la clase Jugador
class Jugador:
    def __init__(self, x, y, salud):
        self.x = x
        self.y = y
        self.salud = salud
        self.velocidad = 5
        self.movimiento = {"arriba": False, "abajo": False, "izquierda": False, "derecha": False}
        self.atacando = False

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
        pygame.draw.rect(pantalla, AZUL, (self.x, self.y, 50, 50))
        self.dibujar_barra_vida(pantalla)

    def dibujar_barra_vida(self, pantalla):
        barra_ancho = 50
        barra_alto = 5
        porcentaje = self.salud / 100
        pygame.draw.rect(pantalla, NEGRO, (self.x, self.y - 10, barra_ancho, barra_alto))
        pygame.draw.rect(pantalla, VERDE if porcentaje > 0.2 else ROJO, 
                         (self.x, self.y - 10, barra_ancho * porcentaje, barra_alto))

    def actualizar_movimiento(self, tecla, presionada):
        if tecla == pygame.K_w:
            self.movimiento["arriba"] = presionada
        elif tecla == pygame.K_s:
            self.movimiento["abajo"] = presionada
        elif tecla == pygame.K_a:
            self.movimiento["izquierda"] = presionada
        elif tecla == pygame.K_d:
            self.movimiento["derecha"] = presionada

    def atacar(self):
        self.atacando = True

    def detener_ataque(self):
        self.atacando = False

# Clase Cliente
class Cliente:
    def __init__(self, host, puerto):
        self.host = host
        self.puerto = puerto
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.puerto))
        self.jugador = Jugador(400, 300, 100)
        self.enemigos = []

        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Juego Cooperativo")
        self.clock = pygame.time.Clock()
        self.corriendo = True

    def enviar_datos(self):
        while self.corriendo:
            datos = f"{self.jugador.x},{self.jugador.y},{self.jugador.salud},{int(self.jugador.atacando)}"
            self.socket.sendall(datos.encode('utf-8'))
            self.jugador.detener_ataque()
            time.sleep(0.05)

    def recibir_datos(self):
        while self.corriendo:
            try:
                datos = self.socket.recv(2048).decode('utf-8')
                if datos:
                    partes = datos.split('|')
                    jugadores_data = partes[0].split(';')
                    enemigos_data = partes[1].split(';')

                    self.enemigos = []
                    for enemigo in enemigos_data:
                        if enemigo:
                            x, y, salud = map(int, enemigo.split(','))
                            self.enemigos.append((x, y, salud))
            except:
                break

    def dibujar_enemigos(self):
        for x, y, salud in self.enemigos:
            color = VERDE if salud > 20 else ROJO
            pygame.draw.rect(self.ventana, color, (x, y, 50, 50))
            pygame.draw.rect(self.ventana, NEGRO, (x, y - 10, 50, 5))
            pygame.draw.rect(self.ventana, VERDE if salud > 20 else ROJO, (x, y - 10, (salud / 100) * 50, 5))

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    self.jugador.atacar()
                else:
                    self.jugador.actualizar_movimiento(evento.key, True)
            elif evento.type == pygame.KEYUP:
                if evento.key == pygame.K_SPACE:
                    self.jugador.detener_ataque()
                else:
                    self.jugador.actualizar_movimiento(evento.key, False)

    def actualizar(self):
        self.jugador.mover()
        self.ventana.fill(BLANCO)
        self.jugador.dibujar(self.ventana)
        self.dibujar_enemigos()
        pygame.display.update()

    def ejecutar(self):
        threading.Thread(target=self.enviar_datos, daemon=True).start()
        threading.Thread(target=self.recibir_datos, daemon=True).start()

        while self.corriendo:
            self.manejar_eventos()
            self.actualizar()
            self.clock.tick(60)

        pygame.quit()
        self.socket.close()

if __name__ == "__main__":
    cliente = Cliente('127.0.0.1', 5555)
    cliente.ejecutar()
