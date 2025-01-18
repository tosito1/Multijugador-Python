import socket
import pygame
import threading

class Cliente:
    def __init__(self, host, puerto):
        self.host = host
        self.puerto = puerto
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.puerto))
        self.jugadores = []
        self.jugador = (100, 100, 100, False, False)
        self.corriendo = True

        # Configurar Pygame
        pygame.init()
        self.ventana = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Juego Multijugador")

    def recibir_posiciones(self):
        while self.corriendo:
            try:
                mensaje = self.socket.recv(1024).decode('utf-8')
                if mensaje:
                    self.jugadores = [tuple(map(int, jugador.split(','))) for jugador in mensaje.split('|')]
            except Exception as e:
                print(f"Error al recibir datos: {e}")
                break

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    self.jugador = (self.jugador[0], self.jugador[1], self.jugador[2], True, self.jugador[4])
                elif evento.key == pygame.K_d:
                    self.jugador = (self.jugador[0], self.jugador[1], self.jugador[2], self.jugador[3], True)
            elif evento.type == pygame.KEYUP:
                if evento.key == pygame.K_SPACE:
                    self.jugador = (self.jugador[0], self.jugador[1], self.jugador[2], False, self.jugador[4])
                elif evento.key == pygame.K_d:
                    self.jugador = (self.jugador[0], self.jugador[1], self.jugador[2], self.jugador[3], False)

    def mover_jugador(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            self.jugador = (self.jugador[0] - 5, self.jugador[1], self.jugador[2], self.jugador[3], self.jugador[4])
        if teclas[pygame.K_RIGHT]:
            self.jugador = (self.jugador[0] + 5, self.jugador[1], self.jugador[2], self.jugador[3], self.jugador[4])
        if teclas[pygame.K_UP]:
            self.jugador = (self.jugador[0], self.jugador[1] - 5, self.jugador[2], self.jugador[3], self.jugador[4])
        if teclas[pygame.K_DOWN]:
            self.jugador = (self.jugador[0], self.jugador[1] + 5, self.jugador[2], self.jugador[3], self.jugador[4])

    def enviar_datos(self):
        datos = f"{self.jugador[0]},{self.jugador[1]},{self.jugador[2]},{int(self.jugador[3])},{int(self.jugador[4])}"
        self.socket.sendall(datos.encode('utf-8'))

    def dibujar_jugador(self):
        pygame.draw.rect(self.ventana, (255, 0, 0), (self.jugador[0], self.jugador[1], 50, 50))

    def dibujar_otros_jugadores(self):
        for x, y, salud, _, _ in self.jugadores:
            pygame.draw.circle(self.ventana, (0, 255, 0), (x, y), 25)

    def run(self):
        threading.Thread(target=self.recibir_posiciones, daemon=True).start()

        while self.corriendo:
            self.ventana.fill((0, 0, 0))  # Limpiar la pantalla

            self.manejar_eventos()  # Manejar eventos del teclado
            self.mover_jugador()  # Actualizar la posición del jugador
            self.enviar_datos()  # Enviar datos al servidor
            self.dibujar_jugador()  # Dibujar al jugador en la pantalla
            self.dibujar_otros_jugadores()  # Dibujar los otros jugadores en la pantalla

            pygame.display.flip()  # Actualizar la pantalla
            pygame.time.Clock().tick(60)  # Limitar los FPS

        self.socket.close()  # Cerrar la conexión al terminar el juego

# Inicializar el cliente
if __name__ == "__main__":
    cliente = Cliente('127.0.0.1', 5555)
    cliente.run()
