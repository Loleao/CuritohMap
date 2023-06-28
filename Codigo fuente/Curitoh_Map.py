import pandas as pd
import networkx as nx
import tkinter as tk
from tkinter import messagebox
import tkintermapview
from tkinter import ttk
from ttkthemes import ThemedTk
import matplotlib.pyplot as plt

class Curitoh:
    def __init__(self):
        self.df = pd.read_csv('dataset.csv', encoding='latin-1')
        self.grafo = nx.from_pandas_edgelist(self.df, source='Inicio', target='Fin', edge_attr='Distancia')

        self.menu = ThemedTk(theme="adapta")
        self.menu.geometry("800x400")
        self.menu.title("Curitoh Map")
        self.menu.configure(background="#28343a")

        self.tbInicio = ttk.Entry(self.menu, style="Custom.TEntry")
        self.tbFin = ttk.Entry(self.menu, style="Custom.TEntry")
        self.tbObligatorio = ttk.Entry(self.menu, state=tk.DISABLED, style="Custom.TEntry")
        self.cbObligatorio = tk.IntVar()
        self.chbObligatorio = ttk.Checkbutton(self.menu, text="¿Quieres usar una direccion obligatoria?", variable=self.cbObligatorio, command=self.control_checkbox_obligatorio, style="Custom.TCheckbutton")

        self.tbIgnorar = ttk.Entry(self.menu, state=tk.DISABLED, style="Custom.TEntry")
        self.cbIgnorar = tk.IntVar()
        self.chbignorar = ttk.Checkbutton(self.menu, text="¿Quieres evitar una direccion?", variable=self.cbIgnorar, command=self.control_checkbox_ignorar, style="Custom.TCheckbutton")

        self.lblInicio = ttk.Label(self.menu, text="Inicio", style="Custom.TLabel")
        self.lblFin = ttk.Label(self.menu, text="Fin", style="Custom.TLabel")

        self.btnMapa = ttk.Button(self.menu, text="Mostrar Mapa", command=self.mostrar_mapa)

        style = ttk.Style()
        style.configure("Custom.TEntry", background="#28343a", foreground="#000000", selectbackground="#1ee9b7", selectforeground="#ffffff", font=("Helvetica", 15))
        style.configure("Custom.TLabel", background="#28343a", foreground="#ffffff", font=("Helvetica", 13))
        style.configure("Custom.TCheckbutton", foreground="#ffffff", background="#28343a", troughcolor="#23444c", font=("Helvetica", 13))

        self.lblInicio.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.lblFin.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.tbInicio.grid(row=0, column=1, padx=5, pady=5, ipadx=75, sticky="e")
        self.chbObligatorio.grid(row=2, column=0, padx=5, pady=5, ipadx=43, sticky="e")
        self.tbObligatorio.grid(row=2, column=1, padx=5, pady=5, ipadx=75, sticky="w")
        self.tbFin.grid(row=1, column=1, padx=5, pady=5, ipadx=75, sticky="e")
        self.chbignorar.grid(row=3, column=0, padx=5, pady=5, ipadx=79, sticky="e")
        self.tbIgnorar.grid(row=3, column=1, padx=5, pady=5, ipadx=75, sticky="w")
        self.btnMapa.grid(row=4, column=1, padx=5, pady=5, ipadx=25)

        self.menu.mainloop()

    def validar_punto_obligatorio(self, punto):
        if punto == '':
            return True
        elif punto in self.df['Inicio'].values:
            return True
        else:
            return False

    def control_checkbox_obligatorio(self):
        if self.cbObligatorio.get() == 1:
            self.tbObligatorio.config(state=tk.NORMAL)
            self.tbIgnorar.config(state=tk.DISABLED)
        else:
            self.tbObligatorio.delete(0, tk.END)
            self.tbObligatorio.config(state=tk.DISABLED)
            self.tbIgnorar.config(state=tk.NORMAL)

    def control_checkbox_ignorar(self):
        if self.cbIgnorar.get() == 1:
            self.tbIgnorar.config(state=tk.NORMAL)
        else:
            self.tbIgnorar.delete(0, tk.END)
            self.tbIgnorar.config(state=tk.DISABLED)

    def mostrar_mapa(self):
        inicio = self.tbInicio.get()
        fin = self.tbFin.get()
        punto_obligatorio = self.tbObligatorio.get()
        punto_ignorar = self.tbIgnorar.get()

        if self.validar_punto_obligatorio(punto_obligatorio):
            if punto_obligatorio != '':
                djk_path_partida = nx.dijkstra_path(self.grafo, source=inicio, target=punto_obligatorio, weight='Distancia')
                djk_path_destino = nx.dijkstra_path(self.grafo, source=punto_obligatorio, target=fin, weight='Distancia')

                if punto_obligatorio in djk_path_partida and punto_obligatorio in djk_path_destino:
                    djk_path_partida.remove(punto_obligatorio)

                djk_path = djk_path_partida + djk_path_destino
            else:
                djk_path = nx.dijkstra_path(self.grafo, source=inicio, target=fin, weight='Distancia')

            num_nodes = len(djk_path)

            if num_nodes >= 2:
                if punto_ignorar != '':
                    new_path = nx.dijkstra_path(self.grafo, source=inicio, target=fin, weight='Distancia')
                    if punto_ignorar in new_path:
                        new_path.remove(punto_ignorar)

                    if len(new_path) < num_nodes:
                        djk_path = new_path
                        num_nodes = len(djk_path)   

                mapa = tk.Toplevel()
                mapa.geometry(f"{1000}x700")
                mapa.title("Curitoh Map")

                ventana_mapa = tkintermapview.TkinterMapView(mapa, width=500, height=700, corner_radius=0)
                ventana_mapa.pack(side=tk.LEFT, fill="both", expand=True)
                coordenadas = []

                for i in range(num_nodes):
                    node = djk_path[i]
                    lat = self.df.at[self.df.loc[self.df['Inicio'] == node].index[0], 'Latitud']
                    lon = self.df.at[self.df.loc[self.df['Inicio'] == node].index[0], 'Longitud']
                    punto = ventana_mapa.set_marker(lat, lon, text=(node + ", Peru"))
                    coordenadas.append(punto.position)

                    if i > 0:
                        ventana_mapa.set_path([coordenadas[i - 1], coordenadas[i]])

                ventana_mapa.set_position(coordenadas[0][0], coordenadas[0][1])
                ventana_mapa.set_zoom(13)

                grafo_djk = nx.DiGraph()
                for i in range(len(djk_path)):
                    grafo_djk.add_node(djk_path[i])

                for i in range(len(djk_path) - 1):
                    grafo_djk.add_edge(djk_path[i], djk_path[i+1], weight=1)
                
                plt.figure(figsize=(5, 7))
                pos = nx.spring_layout(grafo_djk)
                nx.draw(grafo_djk, pos, with_labels=True, node_size=200, node_color='skyblue', font_size=8, font_color='black', edge_color='gray',arrows=False)
                plt.title("Grafo del camino")
                plt.show()

        else:
            messagebox.showerror("Error", "La direccion obligatoria no es válida.")

Curitoh()