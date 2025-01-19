import pygame
import socket
import threading

class Cliente:
    def __init__(self, host, puerto):
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((host, puerto))
        self.jugador = {"x": 100, "y": 100, "salud": 100}  # Posición y salud inicial
        self.enemigos = []  # Lista de enemigos recibida del servidor
        self.jugadores = {}  # Información de otros jugadores
        self.ataques = []  # Lista de ataques realizados por el jugador
        self.corriendo = True

    def enviar_datos(self):
        while self.corriendo:
            try:
                ataques = ';'.join([f"{a[0]},{a[1]}" for a in self.ataques])
                datos = f"{self.jugador['x']},{self.jugador['y']},{self.jugador['salud']}|{ataques}"
                self.cliente.sendall(datos.encode())
                self.ataques = []  # Reiniciar ataques después de enviar
                pygame.time.delay(100)
            except:
                print("Error al enviar datos al servidor.")
                break

    def recibir_datos(self):
        while self.corriendo:
            try:
                datos = self.cliente.recv(1024).decode()
                if datos:
                    enemigos_datos, jugadores_datos = datos.split('|')
                    self.enemigos = [tuple(map(int, e.split(','))) for e in enemigos_datos.split(';') if e]
                    self.jugadores = {int(j.split(',')[0]): tuple(map(int, j.split(',')[1:]))
                                    for j in jugadores_datos.split(';') if j}
                else:
                    print("Conexión cerrada por el servidor.")
                    break
            except socket.error as e:
                print(f"Error al recibir datos del servidor: {e}")
                break
            except Exception as e:
                print(f"Error inesperado: {e}")
                break

    def dibujar(self, ventana):
        ventana.fill((255, 255, 255))  # Fondo blanco
        # Dibujar al jugador
        pygame.draw.rect(ventana, (0, 0, 255), (self.jugador["x"], self.jugador["y"], 50, 50))
        # Dibujar enemigos
        for enemigo in self.enemigos:
            pygame.draw.rect(ventana, (255, 0, 0), (enemigo[0], enemigo[1], 50, 50))
        # Dibujar otros jugadores
        for jugador_id, jugador in self.jugadores.items():
            if jugador_id != id(self.jugador):  # No dibujar al propio jugador
                pygame.draw.rect(ventana, (0, 255, 0), (jugador[0], jugador[1], 50, 50))
        # Mostrar la salud del jugador
        fuente = pygame.font.SysFont("Arial", 20)
        texto_salud = fuente.render(f"Salud: {self.jugador['salud']}", True, (0, 0, 0))
        ventana.blit(texto_salud, (10, 10))
        pygame.display.flip()

    def manejar_eventos(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.jugador["x"] -= 5
        if keys[pygame.K_RIGHT]:
            self.jugador["x"] += 5
        if keys[pygame.K_UP]:
            self.jugador["y"] -= 5
        if keys[pygame.K_DOWN]:
            self.jugador["y"] += 5
        if keys[pygame.K_SPACE]:
            # Registrar un ataque en las coordenadas actuales
            self.ataques.append((self.jugador["x"], self.jugador["y"]))

    def cerrar(self):
        self.corriendo = False
        self.cliente.close()

def main():
    # Configuración inicial de Pygame
    pygame.init()
    ventana = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Cliente Multijugador")
    reloj = pygame.time.Clock()

    # Conectar al servidor
    cliente = Cliente('127.0.0.1', 5555)

    # Hilos para enviar y recibir datos
    hilo_envio = threading.Thread(target=cliente.enviar_datos)
    hilo_recepcion = threading.Thread(target=cliente.recibir_datos)
    hilo_envio.start()
    hilo_recepcion.start()

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

        # Manejar los eventos del teclado
        cliente.manejar_eventos()

        # Dibujar la ventana
        cliente.dibujar(ventana)

        reloj.tick(30)  # Limitar a 30 FPS

    cliente.cerrar()
    hilo_envio.join()
    hilo_recepcion.join()
    pygame.quit()

if __name__ == "__main__":
    main()
