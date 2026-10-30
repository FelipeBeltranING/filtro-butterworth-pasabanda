"""
Filtro Butterworth pasabanda aplicado a voz capturada por micrófono.

Flujo: grabar voz -> filtrar -> reproducir original y filtrada -> graficar espectros.
"""
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

from diseno import disenar_pasabanda
from filtrado import filtrar, respuesta_frecuencia, espectro

# Parámetros del filtro
FS = 44100          # frecuencia de muestreo (Hz)
FC1 = 1000          # frecuencia de corte inferior (Hz)
FC2 = 3500          # frecuencia de corte superior (Hz)
DURACION = 3        # duración de la grabación (s)
F_MAX = 8000        # frecuencia máxima a graficar (Hz)
PASO = 5            # resolución de las gráficas de espectro (Hz)


def grabar(duracion, fs):
    input(f"Presiona Enter y habla durante {duracion} s...")
    print("Grabando...")
    x = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype="float64")
    sd.wait()
    print("Grabación terminada.")
    return x[:, 0]


def reproducir(señal, fs, mensaje):
    print(mensaje)
    sd.play(señal, fs)
    sd.wait()


def graficar(frecuencias, H, X, Y):
    fig, ejes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    titulos = [
        f"Respuesta en frecuencia del filtro ||H(Ω)||  (fc1 = {FC1} Hz, fc2 = {FC2} Hz)",
        "Espectro de la señal de entrada (sin filtrar) ||X(Ω)||",
        "Espectro de la señal filtrada ||Y(Ω)||",
    ]
    datos = [H, X, Y]
    colores = ["tab:green", "tab:blue", "tab:red"]

    for eje, titulo, dato, color in zip(ejes, titulos, datos, colores):
        eje.plot(frecuencias, dato, color=color, linewidth=0.8)
        eje.axvspan(FC1, FC2, color="gold", alpha=0.2, label="Banda de paso")
        eje.axvline(FC1, color="k", linestyle="--", linewidth=0.8)
        eje.axvline(FC2, color="k", linestyle="--", linewidth=0.8)
        eje.set_title(titulo)
        eje.set_ylabel("Magnitud")
        eje.grid(True, alpha=0.3)
        eje.legend(loc="upper right")

    ejes[0].axhline(1 / np.sqrt(2), color="gray", linestyle=":", label="-3 dB")
    ejes[0].legend(loc="upper right")
    ejes[2].set_ylim(ejes[1].get_ylim())   # misma escala para comparar
    ejes[2].set_xlabel("Frecuencia (Hz)")
    plt.tight_layout()
    plt.show()


def main():
    num, den = disenar_pasabanda(FC1, FC2, FS)
    print("Coeficientes del numerador (x):  ", num)
    print("Coeficientes del denominador (y):", den)

    x = grabar(DURACION, FS)
    y = filtrar(x, num, den)

    reproducir(x, FS, "Reproduciendo señal original...")
    reproducir(y, FS, "Reproduciendo señal filtrada...")

    print("Calculando espectros...")
    frecuencias = np.arange(0, F_MAX + PASO, PASO)
    H = respuesta_frecuencia(num, den, frecuencias, FS)
    X = espectro(x, frecuencias, FS)
    Y = espectro(y, frecuencias, FS)
    graficar(frecuencias, H, X, Y)


if __name__ == "__main__":
    main()