"""
FILTRADO POR ECUACIÓN EN DIFERENCIAS Y ANÁLISIS EN FRECUENCIA

Paso 6. Ecuación en diferencias (transformada Z inversa de Y(z)/X(z)):
            y(n) = b0 x(n) + b2 x(n-2) + b4 x(n-4)
                   - a1 y(n-1) - a2 y(n-2) - a3 y(n-3) - a4 y(n-4)

Respuesta en frecuencia:  H(Omega) = sum(b_k e^{-jk Omega}) / sum(a_k e^{-jk Omega})
Espectro de una señal:    X(Omega) = sum_n x(n) e^{-jn Omega}
"""
import math
import numpy as np


def filtrar(x, num, den):
    """Paso 6. Ecuación en diferencias aplicada muestra por muestra."""
    # Condiciones iniciales en cero: x(-1)...x(-4) = 0 y y(-1)...y(-4) = 0
    x = [0.0] * 4 + list(x)
    y = [0.0] * len(x)
    for n in range(4, len(x)):
        y[n] = (num[0] * x[n] + num[2] * x[n - 2] + num[4] * x[n - 4]
                - den[1] * y[n - 1] - den[2] * y[n - 2]
                - den[3] * y[n - 3] - den[4] * y[n - 4])
    return y[4:]


def respuesta_frecuencia(num, den, frecuencias, fs):
    """
    ||H(Omega)|| con Omega = 2 pi f / fs y
    H(Omega) = sum(b_k e^{-jk Omega}) / sum(a_k e^{-jk Omega})
    """
    magnitudes = []
    for f in frecuencias:
        Om = 2 * math.pi * f / fs
        re_n = sum(num[k] * math.cos(k * Om) for k in range(5))
        im_n = -sum(num[k] * math.sin(k * Om) for k in range(5))
        re_d = sum(den[k] * math.cos(k * Om) for k in range(5))
        im_d = -sum(den[k] * math.sin(k * Om) for k in range(5))
        magnitudes.append(math.sqrt(re_n ** 2 + im_n ** 2)
                          / math.sqrt(re_d ** 2 + im_d ** 2))
    return magnitudes


def espectro(x, frecuencias, fs):
    """
    ||X(Omega)|| = sqrt(Re(X)^2 + Im(X)^2) con
    X(Omega) = sum_n x(n) e^{-jn Omega} = sum_n x(n) (cos(n Omega) - j sen(n Omega))
    """
    x = np.asarray(x, dtype=float)
    n = np.arange(len(x))
    magnitudes = []
    for f in frecuencias:
        Om = 2 * math.pi * f / fs
        re = np.sum(x * np.cos(n * Om))
        im = -np.sum(x * np.sin(n * Om))
        magnitudes.append(math.sqrt(re ** 2 + im ** 2))
    return magnitudes


if __name__ == "__main__":
    # Ejemplo: filtrar x(n) = [1, -1, 2] con el filtro fc1 = 1000 Hz, fc2 = 3500 Hz, fs = 44100 Hz
    from diseno import disenar_filtro
    num, den = disenar_filtro(1000, 3500, 44100)
    print("y(n) =", filtrar([1, -1, 2], num, den))
    print("||H|| en fc1 y fc2 =", respuesta_frecuencia(num, den, [1000, 3500], 44100))