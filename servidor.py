import socket
import threading
import time
import random
from enemigos import Enemigo

class Servidor:
    def __init__(self, host, puerto):
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((host, puerto))
        self.servidor.listen()
        print("Servidor en espera de conexiones...")
        self.jugadores = {}  # Diccionario de jugadores: {id: {'x': x, 'y': y, 'salud': salud}}
        self.enemigos = []
        self.oleada = 0
        self.lock = threading.Lock()

    def manejar_cliente(self, conexion, direccion):
        jugador_id = len(self.jugadores) + 1
        # Cambiar a diccionario para los jugadores
        self.jugadores[jugador_id] = {'x': random.randint(50, 750), 'y': random.randint(50, 550), 'salud': 100}  # Posición inicial y salud
        print(f"Jugador {jugador_id} conectado desde {direccion}")

        try:
            while True:
                datos = conexion.recv(1024).decode()
                if not datos:
                    break

                # Procesar datos del cliente
                partes = datos.split('|')
                x, y, salud = map(int, partes[0].split(','))  # Posición y salud
                ataques = [tuple(map(int, a.split(','))) for a in partes[1].split(';') if a]  # Ataques enviados por el jugador

                with self.lock:
                    # Cambiar la forma de asignar la posición y salud
                    self.jugadores[jugador_id] = {'x': x, 'y': y, 'salud': salud}

                    # Procesar ataques a enemigos
                    for ataque in ataques:
                        for enemigo in self.enemigos:
                            if abs(ataque[0] - enemigo.x) < 50 and abs(ataque[1] - enemigo.y) < 50:
                                enemigo.salud -= 25  # Daño al enemigo

                    # Eliminar enemigos muertos
                    self.enemigos = [e for e in self.enemigos if e.salud > 0]

                # Enviar datos de jugadores y enemigos
                enemigos_datos = ';'.join([f"{e.x},{e.y},{e.salud}" for e in self.enemigos])
                jugadores_datos = ';'.join([f"{k},{v['x']},{v['y']},{v['salud']}" for k, v in self.jugadores.items()])
                conexion.sendall(f"{enemigos_datos}|{jugadores_datos}".encode())

        except Exception as e:
            print(f"Error con jugador {jugador_id}: {e}")
        finally:
            with self.lock:
                del self.jugadores[jugador_id]
            print(f"Jugador {jugador_id} desconectado")
            conexion.close()

    def iniciar_oleadas(self):
        while True:
            time.sleep(10)  # Tiempo entre oleadas
            self.oleada += 1
            print(f"Iniciando oleada {self.oleada}")
            num_enemigos = self.oleada * 2
            for _ in range(num_enemigos):
                enemigo = Enemigo(random.randint(0, 800), random.randint(0, 600), 100, random.randint(1, 3))
                self.enemigos.append(enemigo)

    def actualizar_enemigos(self):
            while True:
                time.sleep(0.1)  # Actualización cada 100 ms
                with self.lock:
                    for enemigo in self.enemigos:
                        # Mover enemigo hacia el jugador más cercano
                        if self.jugadores:
                            # Corregir el acceso a las coordenadas del jugador
                            jugador_cercano = min(self.jugadores.values(), key=lambda j: ((j['x'] - enemigo.x) ** 2 + (j['y'] - enemigo.y) ** 2) ** 0.5)
                            enemigo.mover_hacia(jugador_cercano['x'], jugador_cercano['y'])

                        # Ataque a jugadores
                        for jugador_id, jugador in self.jugadores.items():
                            if abs(enemigo.x - jugador['x']) < 50 and abs(enemigo.y - jugador['y']) < 50:
                                nuevo_salud = max(jugador['salud'] - 10, 0)
                                self.jugadores[jugador_id] = {'x': jugador['x'], 'y': jugador['y'], 'salud': nuevo_salud}

                    # Eliminar enemigos muertos
                    self.enemigos = [e for e in self.enemigos if e.salud > 0]

    def iniciar(self):
        threading.Thread(target=self.iniciar_oleadas, daemon=True).start()
        threading.Thread(target=self.actualizar_enemigos, daemon=True).start()

        while True:
            conexion, direccion = self.servidor.accept()
            threading.Thread(target=self.manejar_cliente, args=(conexion, direccion), daemon=True).start()

if __name__ == "__main__":
    servidor = Servidor("127.0.0.1", 5555)
    servidor.iniciar()
