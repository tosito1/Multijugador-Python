import socket
import threading
import tkinter as tk
from tkinter import messagebox

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

                # Actualizar la lista de jugadores
                estado_jugadores = "|".join([f"{x},{y},{salud},{int(atacando)},{int(defendiendo)}" for x, y, salud, atacando, defendiendo in self.jugadores.values()])
                cliente_socket.sendall(estado_jugadores.encode('utf-8'))

        except (ConnectionResetError, BrokenPipeError):
            print(f"Jugador {jugador_id} desconectado.")
        finally:
            if jugador_id in self.jugadores:
                del self.jugadores[jugador_id]
            self.actualizar_lista_jugadores()
            cliente_socket.close()

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
