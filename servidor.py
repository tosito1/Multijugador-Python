import socket
import threading
import random
import time

class Enemigo:
    def __init__(self, x, y, salud):
        self.x = x
        self.y = y
        self.salud = salud

    def mover(self, jugadores):
        """
        Mueve al enemigo hacia el jugador más cercano.
        """
        if jugadores:
            jugador_cercano = min(jugadores, key=lambda j: abs(self.x - j[0]) + abs(self.y - j[1]))
            if self.x < jugador_cercano[0]:
                self.x += 2  # Velocidad del enemigo
            elif self.x > jugador_cercano[0]:
                self.x -= 2
            if self.y < jugador_cercano[1]:
                self.y += 2
            elif self.y > jugador_cercano[1]:
                self.y -= 2

class Servidor:
    def __init__(self, host, puerto):
        self.host = host
        self.puerto = puerto
        self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor_socket.bind((self.host, self.puerto))
        self.servidor_socket.listen(5)

        self.jugadores = {}  # {id: (x, y, salud)}
        self.enemigos = []
        self.oleada_actual = 1
        self.servidor_activo = True

        threading.Thread(target=self.manejar_oleadas, daemon=True).start()

    def manejar_cliente(self, cliente_socket, id_jugador):
        """
        Manejador para cada cliente conectado.
        """
        self.jugadores[id_jugador] = (50, 50, 100)  # Posición inicial (x, y, salud)

        try:
            while True:
                datos = cliente_socket.recv(1024).decode('utf-8')
                if not datos:
                    break
                
                # Depuración: imprimir los datos recibidos
                print(f"Jugador {id_jugador} envió: {datos}")

                # Validar y procesar datos
                partes = datos.split(',')
                if len(partes) == 3:
                    try:
                        x, y, salud = map(int, partes)
                        self.jugadores[id_jugador] = (x, y, salud)
                    except ValueError:
                        print(f"Error al convertir los datos del jugador {id_jugador}: {datos}")
                else:
                    print(f"Formato inválido recibido de jugador {id_jugador}: {datos}")

                # Enviar datos de jugadores y enemigos a todos los clientes
                estado_jugadores = "|".join([f"{x},{y},{salud}" for x, y, salud in self.jugadores.values()])
                estado_enemigos = "|".join([f"{e.x},{e.y},{e.salud}" for e in self.enemigos])
                cliente_socket.sendall(f"{estado_jugadores}#ENEMIGOS#{estado_enemigos}".encode('utf-8'))
        except (ConnectionResetError, BrokenPipeError):
            print(f"Jugador {id_jugador} desconectado.")
        finally:
            if id_jugador in self.jugadores:
                del self.jugadores[id_jugador]
            cliente_socket.close()


    def manejar_oleadas(self):
        """
        Controla las oleadas de enemigos.
        """
        while self.servidor_activo:
            if not self.enemigos:  # Nueva oleada si no hay enemigos
                self.oleada_actual += 1
                print(f"Iniciando oleada {self.oleada_actual}")
                for _ in range(self.oleada_actual * 5):  # Más enemigos con cada oleada
                    x = random.randint(0, 800)
                    y = random.randint(0, 600)
                    self.enemigos.append(Enemigo(x, y, 50))

            # Mover enemigos
            jugadores = list(self.jugadores.values())
            for enemigo in self.enemigos[:]:  # Copia para evitar problemas al eliminar
                enemigo.mover(jugadores)
                if enemigo.salud <= 0:
                    self.enemigos.remove(enemigo)

            time.sleep(0.05)  # Control de velocidad de actualización

    def iniciar(self):
        print("Servidor en espera de conexiones...")
        while self.servidor_activo:
            cliente_socket, _ = self.servidor_socket.accept()
            id_jugador = len(self.jugadores) + 1
            print(f"Jugador {id_jugador} conectado.")
            threading.Thread(target=self.manejar_cliente, args=(cliente_socket, id_jugador), daemon=True).start()

if __name__ == "__main__":
    servidor = Servidor('127.0.0.1', 5555)
    servidor.iniciar()
