"""
DISEÑO DEL FILTRO BUTTERWORTH PASABANDA DE ORDEN 2
POR TRANSFORMACIÓN BILINEAL

Paso 1. Prototipo normalizado de orden 2:
            H(s) = 1 / (s^2 + sqrt(2) s + 1)

Paso 2. Transformación pasabanda  s <- (s^2 + w0^2) / (BW s):
            HBP(s) = BW^2 s^2 / (s^4 + sqrt(2) BW s^3 + (2 w0^2 + BW^2) s^2
                                 + sqrt(2) BW w0^2 s + w0^4)
            w0 = sqrt(wc1 wc2)      BW = wc2 - wc1

Paso 3. Prewarping:
            wd = (2/T) tan(pi fc / fs)

Paso 4. Transformación bilineal:
            s = (2/T) (1 - z^-1) / (1 + z^-1)
        Todos los factores 2/T se cancelan y se multiplica numerador y
        denominador por (1 + z^-1)^4.

Paso 5. Se normaliza dividiendo entre d0.
"""
import math


def disenar_filtro(fc1, fc2, fs):
    """Obtiene los coeficientes de la ecuación en diferencias (pasos 3 a 5)."""

    # Paso 3. Prewarping: wd1 = (2/T) a,  wd2 = (2/T) b
    a = math.tan(math.pi * fc1 / fs)
    b = math.tan(math.pi * fc2 / fs)

    # w0^2 = (2/T)^2 a b  y  BW = (2/T)(b - a); sin el factor 2/T quedan:
    B = b - a          # ancho de banda
    W = a * b          # w0^2

    # Constantes del denominador de HBP
    A = math.sqrt(2) * B          # sqrt(2) BW
    C = 2 * W + B ** 2            # 2 w0^2 + BW^2
    D = math.sqrt(2) * B * W      # sqrt(2) BW w0^2
    E = W ** 2                    # w0^4

    # Paso 4. Bilineal y agrupación por potencias de z^-1
    # Numerador: B^2 (1 - z^-1)^2 (1 + z^-1)^2 = B^2 (1 - 2 z^-2 + z^-4)
    n0 = B ** 2
    n2 = -2 * B ** 2
    n4 = B ** 2

    # Denominador
    d0 = 1 + A + C + D + E
    d1 = -4 - 2 * A + 2 * D + 4 * E
    d2 = 6 - 2 * C + 6 * E
    d3 = -4 + 2 * A - 2 * D + 4 * E
    d4 = 1 - A + C - D + E

    # Paso 5. Normalización entre d0
    num = [n0 / d0, 0.0, n2 / d0, 0.0, n4 / d0]           # b0, b1, b2, b3, b4
    den = [1.0, d1 / d0, d2 / d0, d3 / d0, d4 / d0]       # 1, a1, a2, a3, a4

    return {
        "a": a, "b": b, "B": B, "W": W,
        "A": A, "C": C, "D": D, "E": E,
        "n": [n0, 0.0, n2, 0.0, n4],
        "d": [d0, d1, d2, d3, d4],
        "num": num, "den": den,
    }


if __name__ == "__main__":
    # Comprobación del diseño a mano con fc1 = 1000 Hz, fc2 = 3500 Hz, fs = 44100 Hz
    f = disenar_filtro(1000, 3500, 44100)
    for clave in ["a", "b", "B", "W", "A", "C", "D", "E"]:
        print(f"{clave} = {f[clave]:.6f}")
    print("n =", [round(v, 6) for v in f["n"]])
    print("d =", [round(v, 6) for v in f["d"]])
    print("num =", [round(v, 6) for v in f["num"]])
    print("den =", [round(v, 6) for v in f["den"]])