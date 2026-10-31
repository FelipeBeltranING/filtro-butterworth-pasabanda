"""
Interfaz gráfica del filtro Butterworth pasabanda.

El diseño del filtro está en diseno.py y el filtrado en filtrado.py; este archivo solo
se encarga de la interfaz, el micrófono, la reproducción y las gráficas.
"""
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import sounddevice as sd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from diseno import disenar_filtro
from filtrado import filtrar, respuesta_frecuencia, espectro

F_MAX = 8000     # frecuencia máxima graficada (Hz)
PASO = 5         # resolución de las gráficas (Hz)

COLOR_PASO = "#c8e6c9"
COLOR_RECHAZO = "#ffcdd2"


def valores_intermedios(fc1, fc2, fs):
    """Recalcula los pasos intermedios del diseño solo para mostrarlos en el panel."""
    a = math.tan(math.pi * fc1 / fs)
    b = math.tan(math.pi * fc2 / fs)
    B = b - a
    W = a * b
    A = math.sqrt(2) * B
    C = 2 * W + B ** 2
    D = math.sqrt(2) * B * W
    E = W ** 2
    n = [B ** 2, 0.0, -2 * B ** 2, 0.0, B ** 2]
    d = [1 + A + C + D + E, -4 - 2 * A + 2 * D + 4 * E, 6 - 2 * C + 6 * E,
         -4 + 2 * A - 2 * D + 4 * E, 1 - A + C - D + E]
    return {"a": a, "b": b, "B": B, "W": W, "A": A, "C": C, "D": D, "E": E, "n": n, "d": d}


class Aplicacion:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Filtro Butterworth pasabanda - Transformación bilineal")
        self.raiz.geometry("1350x820")
        self.raiz.minsize(1100, 700)

        self.num = None        # coeficientes b0..b4
        self.den = None        # coeficientes a0..a4
        self.params = None
        self.x = None          # señal grabada
        self.y = None          # señal filtrada

        self._estilos()
        self._construir_panel_izquierdo()
        self._construir_graficas()
        self.disenar()

    # ------------------------------------------------------------------ UI
    def _estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 14, "bold"))
        estilo.configure("Sub.TLabel", font=("Segoe UI", 9), foreground="#555")
        estilo.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        estilo.configure("Accion.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        estilo.configure("TButton", padding=5)
        estilo.configure("Ok.TLabel", foreground="#2e7d32")
        estilo.configure("Error.TLabel", foreground="#c62828")

    def _construir_panel_izquierdo(self):
        panel = ttk.Frame(self.raiz, padding=12)
        panel.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(panel, text="Filtro Butterworth pasabanda",
                  style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(panel, text="Orden 2 · Transformación bilineal",
                  style="Sub.TLabel").pack(anchor="w", pady=(0, 10))

        # Parámetros
        marco = ttk.LabelFrame(panel, text="Parámetros", padding=10)
        marco.pack(fill=tk.X)
        self.var_fs = tk.StringVar(value="44100")
        self.var_fc1 = tk.StringVar(value="1000")
        self.var_fc2 = tk.StringVar(value="3500")
        self.var_dur = tk.StringVar(value="3")
        campos = [("Frecuencia de muestreo fs (Hz)", self.var_fs),
                  ("Frecuencia de corte fc1 (Hz)", self.var_fc1),
                  ("Frecuencia de corte fc2 (Hz)", self.var_fc2),
                  ("Duración de la grabación (s)", self.var_dur)]
        for i, (texto, var) in enumerate(campos):
            ttk.Label(marco, text=texto).grid(row=i, column=0, sticky="w", pady=3)
            ttk.Entry(marco, textvariable=var, width=10,
                      justify="right").grid(row=i, column=1, padx=(8, 0), pady=3)

        self.lbl_bw = ttk.Label(marco, text="")
        self.lbl_bw.grid(row=4, column=0, columnspan=2, sticky="w", pady=(6, 0))
        for var in (self.var_fc1, self.var_fc2):
            var.trace_add("write", lambda *_: self._actualizar_bw())
        self._actualizar_bw()

        self.btn_disenar = ttk.Button(marco, text="Diseñar filtro",
                                      style="Accion.TButton", command=self.disenar)
        self.btn_disenar.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        # Audio
        audio = ttk.LabelFrame(panel, text="Voz", padding=10)
        audio.pack(fill=tk.X, pady=(10, 0))
        self.btn_grabar = ttk.Button(audio, text="●  Grabar voz",
                                     style="Accion.TButton", command=self.grabar)
        self.btn_grabar.pack(fill=tk.X)
        fila = ttk.Frame(audio)
        fila.pack(fill=tk.X, pady=(6, 0))
        self.btn_orig = ttk.Button(fila, text="▶ Original", state=tk.DISABLED,
                                   command=lambda: self.reproducir(self.x))
        self.btn_orig.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.btn_filt = ttk.Button(fila, text="▶ Filtrada", state=tk.DISABLED,
                                   command=lambda: self.reproducir(self.y))
        self.btn_filt.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        ttk.Button(fila, text="■ Detener", command=sd.stop).pack(
            side=tk.LEFT, expand=True, fill=tk.X)

        # Diseño matemático
        diseno = ttk.LabelFrame(panel, text="Diseño matemático", padding=6)
        diseno.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.txt = tk.Text(diseno, width=44, font=("Consolas", 9), relief=tk.FLAT,
                           background="#fafafa", wrap=tk.NONE)
        barra = ttk.Scrollbar(diseno, orient=tk.VERTICAL, command=self.txt.yview)
        self.txt.config(yscrollcommand=barra.set)
        barra.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Estado
        self.lbl_estado = ttk.Label(panel, text="Listo.", style="Sub.TLabel")
        self.lbl_estado.pack(anchor="w", pady=(8, 0))

    def _construir_graficas(self):
        marco = ttk.Frame(self.raiz, padding=(0, 8, 8, 8))
        marco.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.fig = Figure(figsize=(9, 7.5), dpi=100)
        self.ax_h, self.ax_x, self.ax_y = self.fig.subplots(3, 1, sharex=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=marco)
        NavigationToolbar2Tk(self.canvas, marco).update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ---------------------------------------------------------- Parámetros
    def _leer_parametros(self):
        try:
            fs = float(self.var_fs.get())
            fc1 = float(self.var_fc1.get())
            fc2 = float(self.var_fc2.get())
            dur = float(self.var_dur.get())
        except ValueError:
            raise ValueError("Todos los parámetros deben ser números.")
        bw = fc2 - fc1
        if fc1 <= 0 or fc2 <= fc1:
            raise ValueError("Debe cumplirse 0 < fc1 < fc2.")
        if not 2000 <= bw <= 3000:
            raise ValueError(f"El ancho de banda BW = fc2 - fc1 = {bw:g} Hz "
                             "debe estar entre 2000 Hz y 3000 Hz.")
        if fc2 > 5000:
            raise ValueError("Las frecuencias de corte no pueden superar 5000 Hz.")
        if fc2 >= fs / 2:
            raise ValueError("fc2 debe ser menor que fs/2 (frecuencia de Nyquist).")
        if not 1 <= dur <= 10:
            raise ValueError("La duración debe estar entre 1 y 10 segundos.")
        return fs, fc1, fc2, dur

    def _actualizar_bw(self):
        try:
            bw = float(self.var_fc2.get()) - float(self.var_fc1.get())
            fc2 = float(self.var_fc2.get())
        except ValueError:
            self.lbl_bw.config(text="BW = —", style="Error.TLabel")
            return
        ok = 2000 <= bw <= 3000 and fc2 <= 5000
        marca = "(cumple)" if ok else "(debe ser 2000 ≤ BW ≤ 3000 y fc2 ≤ 5000)"
        self.lbl_bw.config(text=f"BW = {bw:g} Hz  {marca}",
                           style="Ok.TLabel" if ok else "Error.TLabel")

    # -------------------------------------------------------------- Acciones
    def disenar(self):
        try:
            self.params = self._leer_parametros()
        except ValueError as e:
            messagebox.showerror("Parámetros no válidos", str(e))
            return
        fs, fc1, fc2, _ = self.params
        self.num, self.den = disenar_filtro(fc1, fc2, fs)
        self._mostrar_diseno()
        if self.x is not None:
            self._procesar()          # vuelve a filtrar la grabación con el nuevo diseño
        else:
            self._graficar(None, None)

    def grabar(self):
        if self.num is None:
            return
        fs, _, _, dur = self.params
        self._ocupado(True, f"Grabando {dur:g} s... habla ahora.")

        def tarea():
            try:
                grab = sd.rec(int(dur * fs), samplerate=int(fs), channels=1, dtype="float64")
                sd.wait()
            except Exception as e:
                self.raiz.after(0, lambda: self._error_audio(e))
                return
            self.x = grab[:, 0]
            self.raiz.after(0, self._procesar)

        threading.Thread(target=tarea, daemon=True).start()

    def _procesar(self):
        fs = self.params[0]
        num, den = self.num, self.den
        self._ocupado(True, "Filtrando y calculando espectros...")

        def tarea():
            y = np.array(filtrar(self.x, num, den))
            frecs = np.arange(0, F_MAX + PASO, PASO)
            X = espectro(self.x, frecs, fs)
            Y = espectro(y, frecs, fs)
            self.y = y
            self.raiz.after(0, lambda: self._terminar_proceso(X, Y))

        threading.Thread(target=tarea, daemon=True).start()

    def _terminar_proceso(self, X, Y):
        self._graficar(X, Y)
        self._ocupado(False, "Listo. Reproduce las señales para comparar.")
        self.btn_orig.config(state=tk.NORMAL)
        self.btn_filt.config(state=tk.NORMAL)

    def reproducir(self, senal):
        if senal is None:
            return
        sd.stop()
        sd.play(senal, int(self.params[0]))

    def _error_audio(self, e):
        self._ocupado(False, "Error con el micrófono.")
        messagebox.showerror("Micrófono", f"No se pudo grabar:\n{e}")

    def _ocupado(self, ocupado, mensaje):
        estado = tk.DISABLED if ocupado else tk.NORMAL
        self.btn_grabar.config(state=estado)
        self.btn_disenar.config(state=estado)
        self.lbl_estado.config(text=mensaje)

    # ------------------------------------------------------------- Mostrar
    def _mostrar_diseno(self):
        fs, fc1, fc2, _ = self.params
        f = valores_intermedios(fc1, fc2, fs)
        n, d, num, den = f["n"], f["d"], self.num, self.den
        t = []
        t.append(f"fs = {fs:g} Hz   fc1 = {fc1:g} Hz   fc2 = {fc2:g} Hz")
        t.append("")
        t.append("1) Prewarping")
        t.append(f"   a = tan(π·fc1/fs) = {f['a']:.6f}")
        t.append(f"   b = tan(π·fc2/fs) = {f['b']:.6f}")
        t.append(f"   B = b − a         = {f['B']:.6f}")
        t.append(f"   W = a·b           = {f['W']:.6f}")
        t.append("")
        t.append("2) Constantes")
        t.append(f"   B² = {n[0]:.6f}")
        t.append(f"   A = √2·B      = {f['A']:.6f}")
        t.append(f"   C = 2W + B²   = {f['C']:.6f}")
        t.append(f"   D = √2·B·W    = {f['D']:.6f}")
        t.append(f"   E = W²        = {f['E']:.6f}")
        t.append("")
        t.append("3) Bilineal: coeficientes de z^-k")
        for k in range(5):
            t.append(f"   n{k} = {n[k]:>10.6f}     d{k} = {d[k]:>10.6f}")
        t.append("")
        t.append(f"4) Normalizado (÷ d0 = {d[0]:.6f})")
        for k in range(5):
            t.append(f"   b{k} = {num[k]:>10.6f}     a{k} = {den[k]:>10.6f}")
        t.append("")
        t.append("5) Ecuación en diferencias")

        def s(v):
            return f"{'+' if v >= 0 else '−'} {abs(v):.6f}"

        t.append(f"   y(n) = {num[0]:.6f} x(n)")
        t.append(f"          {s(num[2])} x(n−2)")
        t.append(f"          {s(num[4])} x(n−4)")
        for k in range(1, 5):
            t.append(f"          {s(-den[k])} y(n−{k})")

        self.txt.config(state=tk.NORMAL)
        self.txt.delete("1.0", tk.END)
        self.txt.insert("1.0", "\n".join(t))
        self.txt.config(state=tk.DISABLED)

    def _sombrear_bandas(self, ax, fc1, fc2, leyenda=False):
        ax.axvspan(0, fc1, color=COLOR_RECHAZO, alpha=0.5,
                   label="Banda de rechazo" if leyenda else None)
        ax.axvspan(fc1, fc2, color=COLOR_PASO, alpha=0.6,
                   label="Banda de paso" if leyenda else None)
        ax.axvspan(fc2, F_MAX, color=COLOR_RECHAZO, alpha=0.5)
        ax.axvline(fc1, color="k", linestyle="--", linewidth=0.8)
        ax.axvline(fc2, color="k", linestyle="--", linewidth=0.8)

    def _graficar(self, X, Y):
        fs, fc1, fc2, _ = self.params
        frecs = np.arange(0, F_MAX + PASO, PASO)
        H = respuesta_frecuencia(self.num, self.den, frecs, fs)

        for ax in (self.ax_h, self.ax_x, self.ax_y):
            ax.clear()

        self._sombrear_bandas(self.ax_h, fc1, fc2, leyenda=True)
        self.ax_h.plot(frecs, H, color="#1b5e20", linewidth=1.4, label="||H(Ω)||")
        self.ax_h.axhline(1 / np.sqrt(2), color="gray", linestyle=":", label="−3 dB (0.707)")
        self.ax_h.set_title(f"Respuesta en frecuencia del filtro  (fc1 = {fc1:g} Hz, fc2 = {fc2:g} Hz)")
        self.ax_h.set_ylim(0, 1.1)
        self.ax_h.legend(loc="upper right", fontsize=8)

        self._sombrear_bandas(self.ax_x, fc1, fc2)
        self._sombrear_bandas(self.ax_y, fc1, fc2)
        self.ax_x.set_title("Espectro de la señal de entrada (sin filtrar)  ||X(Ω)||")
        self.ax_y.set_title("Espectro de la señal filtrada  ||Y(Ω)||")

        if X is None:
            for ax in (self.ax_x, self.ax_y):
                ax.text(0.5, 0.5, "Graba tu voz para ver el espectro",
                        transform=ax.transAxes, ha="center", va="center", color="#777")
        else:
            self.ax_x.plot(frecs, X, color="#1565c0", linewidth=0.7)
            self.ax_y.plot(frecs, Y, color="#c62828", linewidth=0.7)
            tope = max(X) * 1.05
            self.ax_x.set_ylim(0, tope)
            self.ax_y.set_ylim(0, tope)   # misma escala para comparar

        for ax in (self.ax_h, self.ax_x, self.ax_y):
            ax.set_ylabel("Magnitud")
            ax.set_xlim(0, F_MAX)
            ax.grid(True, alpha=0.3)
        self.ax_y.set_xlabel("Frecuencia (Hz)")
        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    raiz = tk.Tk()
    Aplicacion(raiz)
    raiz.mainloop()