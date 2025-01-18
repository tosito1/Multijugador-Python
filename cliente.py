import socket
import threading
from jugador import Jugador

class Cliente:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.jugador = Jugador(100, 100, 100)
        self.jugadores = {}  # Guardar otros jugadores
        self.corriendo = True

    def recibir_posiciones(self):
        while self.corriendo:
            try:
                mensaje = self.socket.recv(1024).decode('utf-8')
                if mensaje:
                    self.procesar_mensaje(mensaje)
            except Exception as e:
                print(f"Error al recibir datos: {e}")
                self.corriendo = False

    def procesar_mensaje(self, mensaje):
        jugadores_info = mensaje.split("|")
        for jugador_info in jugadores_info:
            id, x, y, salud, atacando, defendiendo = map(int, jugador_info.split(","))
            self.jugadores[id] = {"x": x, "y": y, "salud": salud, "atacando": atacando, "defendiendo": defendiendo}

    def enviar_datos(self):
        try:
            datos = f"{self.jugador.x},{self.jugador.y},{self.jugador.salud},{int(self.jugador.atacando)},{int(self.jugador.defendiendo)}"
            self.socket.sendall(datos.encode('utf-8'))
        except Exception as e:
            print(f"Error al enviar datos: {e}")


