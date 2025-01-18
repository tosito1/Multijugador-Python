import socket
import threading
import tkinter as tk
from tkinter import messagebox
import pygame  # Usaremos Pygame para efectos visuales

# Inicializar pygame
pygame.init()

class Servidor:
    def __init__(self, host, puerto):
        self.host = host
        self.puerto = puerto
        self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor_socket.bind((self.host, self.puerto))
        self.servidor_socket.listen(5)
        self.jugadores = {}  # {id: (x, y, salud, atacando, defendiendo)}
        self.servidor_activo = True

        # Interfaz gráfica del servidor
        self.ventana = tk.Tk()
        self.ventana.title("Servidor de Juego")

        self.lista_jugadores = tk.Listbox(self.ventana, height=15, width=50)
        self.lista_jugadores.pack(pady=10)

        self.boton_eliminar = tk.Button(self.ventana, text="Eliminar Jugador", command=self.eliminar_jugador)
        self.boton_eliminar.pack(pady=5)

        self.boton_iniciar = tk.Button(self.ventana, text="Iniciar Partida", command=self.iniciar_partida)
        self.boton_iniciar.pack(pady=5)

        threading.Thread(target=self.aceptar_conexiones, daemon=True).start()

    def aceptar_conexiones(self):
        print("Servidor en espera de conexiones...")
        while self.servidor_activo:
            cliente, direccion = self.servidor_socket.accept()
            print(f"Jugador conectado desde {direccion}")
            threading.Thread(target=self.manejar_cliente, args=(cliente,)).start()

    def manejar_cliente(self, cliente_socket):
        jugador_id = threading.get_ident()  # Usamos el ID del hilo como identificador único del jugador
        self.jugadores[jugador_id] = (50, 50, 100, False, False)  # Posición inicial (x, y) y salud
        self.actualizar_lista_jugadores()

        try:
            while True:
                datos = cliente_socket.recv(1024).decode('utf-8')
                if not datos:
                    break

                # Procesar los datos recibidos
                self.jugadores[jugador_id] = tuple(map(int, datos.split(',')))

                # Verificar ataques y actualizar la salud
                self.procesar_ataques()

                # Actualizar la lista de jugadores
                estado_jugadores = "|".join([f"{x},{y},{salud},{int(atacando)},{int(defendiendo)}" 
                                             for x, y, salud, atacando, defendiendo in self.jugadores.values()])
                cliente_socket.sendall(estado_jugadores.encode('utf-8'))

        except (ConnectionResetError, BrokenPipeError):
            print(f"Jugador {jugador_id} desconectado.")
        finally:
            if jugador_id in self.jugadores:
                del self.jugadores[jugador_id]
            self.actualizar_lista_jugadores()
            cliente_socket.close()

    def procesar_ataques(self):
        """
        Verifica si un jugador está atacando y si hay colisión con otro jugador.
        Si hay colisión, reduce la salud del jugador atacado.
        """
        for jugador_id, (x, y, salud, atacando, defendiendo) in self.jugadores.items():
            if atacando:
                # Mostrar animación de ataque
                self.mostrar_efecto_ataque(jugador_id)

                # Verificar si hay colisión con otro jugador
                for otro_id, (x_otro, y_otro, salud_otro, atacando_otro, defendiendo_otro) in self.jugadores.items():
                    if jugador_id != otro_id:
                        # Comprobamos la proximidad del ataque (ajustar el rango según el juego)
                        if abs(x - x_otro) < 50 and abs(y - y_otro) < 50:
                            if not defendiendo_otro:  # Si el otro jugador no está defendiendo
                                nueva_salud = salud_otro - 20  # Reducir la salud en 20 (ajustable)
                                nueva_salud = max(nueva_salud, 0)  # Asegurarse de que la salud no sea negativa
                                self.jugadores[otro_id] = (x_otro, y_otro, nueva_salud, atacando_otro, defendiendo_otro)
                                print(f"Jugador {otro_id} ha sido atacado. Salud restante: {nueva_salud}")

            if defendiendo:
                # Mostrar animación de defensa
                self.mostrar_efecto_defensa(jugador_id)

    def mostrar_efecto_ataque(self, jugador_id):
        """
        Muestra un efecto visual de ataque en el jugador.
        """
        print(f"Jugador {jugador_id} está atacando! (Visualización de ataque)")

        # Aquí puedes agregar un cambio visual, por ejemplo, cambiar el color del jugador o mostrar una animación

    def mostrar_efecto_defensa(self, jugador_id):
        """
        Muestra un efecto visual de defensa en el jugador.
        """
        print(f"Jugador {jugador_id} está defendiendo! (Visualización de defensa)")

        # Aquí puedes agregar un cambio visual, como poner un borde alrededor del jugador o hacer que se ilumine

    def actualizar_lista_jugadores(self):
        """
        Actualiza la lista de jugadores en la interfaz gráfica del servidor.
        """
        self.lista_jugadores.delete(0, tk.END)
        for jugador_id, (x, y, salud, atacando, defendiendo) in self.jugadores.items():
            self.lista_jugadores.insert(tk.END, f"ID: {jugador_id}, Pos: ({x}, {y}), Salud: {salud}")

    def eliminar_jugador(self):
        """
        Elimina un jugador seleccionado desde la lista de jugadores.
        """
        seleccion = self.lista_jugadores.curselection()
        if seleccion:
            jugador_info = self.lista_jugadores.get(seleccion[0])
            jugador_id = int(jugador_info.split(",")[0].split(": ")[1])
            if jugador_id in self.jugadores:
                del self.jugadores[jugador_id]
                self.actualizar_lista_jugadores()
                messagebox.showinfo("Jugador Eliminado", f"Jugador {jugador_id} eliminado con éxito.")
        else:
            messagebox.showwarning("Selección Inválida", "Por favor, selecciona un jugador para eliminar.")

    def iniciar_partida(self):
        """
        Inicia la partida si hay jugadores conectados.
        """
        if self.jugadores:
            messagebox.showinfo("Partida Iniciada", "La partida ha comenzado.")
        else:
            messagebox.showwarning("Sin Jugadores", "No hay jugadores conectados para iniciar la partida.")

    def iniciar_servidor(self):
        """
        Inicia la interfaz gráfica del servidor.
        """
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar_servidor)
        self.ventana.mainloop()

    def cerrar_servidor(self):
        """
        Cierra el servidor y la ventana.
        """
        self.servidor_activo = False
        self.servidor_socket.close()
        self.ventana.destroy()

# Inicializar el servidor
if __name__ == "__main__":
    servidor = Servidor('127.0.0.1', 5555)
    servidor.iniciar_servidor()
