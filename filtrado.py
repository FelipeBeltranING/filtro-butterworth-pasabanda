"""
Filtrado por ecuación en diferencias y respuesta en frecuencia.

H(z) = Y(z)/X(z) = (b0 + b1 z^-1 + ... + b4 z^-4) / (1 + a1 z^-1 + ... + a4 z^-4)

Aplicando la transformada Z inversa:
    y(n) = b0 x(n) + b1 x(n-1) + ... + b4 x(n-4) - a1 y(n-1) - ... - a4 y(n-4)
"""
import math
import numpy as np


def filtrar(x, num, den):
    """Aplica la ecuación en diferencias muestra por muestra."""
    x = list(x)
    y = [0.0] * len(x)
    for n in range(len(x)):
        suma = 0.0
        for k in range(len(num)):          # parte no recursiva: x(n-k)
            if n - k >= 0:
                suma += num[k] * x[n - k]
        for k in range(1, len(den)):       # parte recursiva: y(n-k)
            if n - k >= 0:
                suma -= den[k] * y[n - k]
        y[n] = suma
    return np.array(y)


def respuesta_frecuencia(num, den, frecuencias, fs):
    """
    ||H(Omega)|| con Omega = 2 pi f / fs y
    H(Omega) = sum(b_k e^{-jk Omega}) / sum(a_k e^{-jk Omega})
    """
    magnitudes = []
    for f in frecuencias:
        W = 2 * math.pi * f / fs
        re_n = sum(num[k] * math.cos(k * W) for k in range(len(num)))
        im_n = -sum(num[k] * math.sin(k * W) for k in range(len(num)))
        re_d = sum(den[k] * math.cos(k * W) for k in range(len(den)))
        im_d = -sum(den[k] * math.sin(k * W) for k in range(len(den)))
        magnitudes.append(math.sqrt(re_n ** 2 + im_n ** 2) /
                          math.sqrt(re_d ** 2 + im_d ** 2))
    return np.array(magnitudes)


def espectro(x, frecuencias, fs):
    """
    ||X(Omega)|| = sqrt(Re(X)^2 + Im(X)^2) con
    X(Omega) = sum_n x(n) e^{-jn Omega} = sum_n x(n) (cos(n Omega) - j sen(n Omega))
    """
    x = np.asarray(x, dtype=float)
    n = np.arange(len(x))
    magnitudes = np.zeros(len(frecuencias))
    for i, f in enumerate(frecuencias):
        W = 2 * math.pi * f / fs
        re = np.sum(x * np.cos(n * W))
        im = -np.sum(x * np.sin(n * W))
        magnitudes[i] = math.sqrt(re ** 2 + im ** 2)
    return magnitudes