"""
Diseño del filtro Butterworth pasabanda de orden 2 por transformación bilineal.

Pasos:
    1. Prewarping de las frecuencias de corte:  wd = (2/T) tan(pi fc / fs)
    2. Transformación pasabanda del prototipo normalizado de orden 2
           H(s) = 1 / (s^2 + sqrt(2) s + 1),   s <- (s^2 + w0^2) / (BW s)
       HBP(s) = BW^2 s^2 / (s^4 + sqrt(2) BW s^3 + (2 w0^2 + BW^2) s^2
                            + sqrt(2) BW w0^2 s + w0^4)
       con w0 = sqrt(wc1 wc2) y BW = wc2 - wc1
    3. Transformación bilineal:  s = (2/T) (1 - z^-1) / (1 + z^-1)
"""
import math


def disenar_pasabanda(fc1, fc2, fs):
    T = 1 / fs

    # 1. Prewarping
    wd1 = (2 / T) * math.tan(math.pi * fc1 / fs)
    wd2 = (2 / T) * math.tan(math.pi * fc2 / fs)

    # 2. Parámetros del pasabanda
    w0 = math.sqrt(wd1 * wd2)
    BW = wd2 - wd1

    # 3. Bilineal: se reemplaza s = (2/T)(1 - z^-1)/(1 + z^-1) en HBP(s)
    #    y se multiplican numerador y denominador por (1 + z^-1)^4.
    #    Polinomios en z^-1 (coeficientes de z^0, z^-1, ..., z^-4):
    P4 = [1, -4, 6, -4, 1]   # (1 - z^-1)^4
    P3 = [1, -2, 0, 2, -1]   # (1 - z^-1)^3 (1 + z^-1)
    P2 = [1, 0, -2, 0, 1]    # (1 - z^-1)^2 (1 + z^-1)^2
    P1 = [1, 2, 0, -2, -1]   # (1 - z^-1)   (1 + z^-1)^3
    P0 = [1, 4, 6, 4, 1]     # (1 + z^-1)^4

    K = 2 / T
    c4 = K ** 4                                  # s^4
    c3 = math.sqrt(2) * BW * K ** 3              # sqrt(2) BW s^3
    c2 = (2 * w0 ** 2 + BW ** 2) * K ** 2        # (2 w0^2 + BW^2) s^2
    c1 = math.sqrt(2) * BW * w0 ** 2 * K         # sqrt(2) BW w0^2 s
    c0 = w0 ** 4                                 # w0^4

    num = [(BW ** 2) * (K ** 2) * P2[k] for k in range(5)]
    den = [c4 * P4[k] + c3 * P3[k] + c2 * P2[k] + c1 * P1[k] + c0 * P0[k]
           for k in range(5)]

    # Se divide todo entre den[0] para que y(n) quede despejado
    d0 = den[0]
    num = [nk / d0 for nk in num]
    den = [dk / d0 for dk in den]
    return num, den


if __name__ == "__main__":
    num, den = disenar_pasabanda(1000, 3500, 44100)
    print("Coeficientes del numerador (x):  ", num)
    print("Coeficientes del denominador (y):", den)