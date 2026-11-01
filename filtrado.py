import math
import numpy as np


def filtrar(x, num, den):

    x = [0.0] * 4 + list(x)
    y = [0.0] * len(x)
    for n in range(4, len(x)):
        y[n] = (num[0] * x[n] + num[2] * x[n - 2] + num[4] * x[n - 4]
                - den[1] * y[n - 1] - den[2] * y[n - 2]
                - den[3] * y[n - 3] - den[4] * y[n - 4])
    return y[4:]         


def respuesta_frecuencia(num, den, frecuencias, fs):
    magnitudes = []
    for f in frecuencias:                 
        Om = 2 * math.pi * f / fs

        re_num = 0.0
        im_num = 0.0
        re_den = 0.0
        im_den = 0.0
        for k in range(5):
            re_num = re_num + num[k] * math.cos(k * Om)
            im_num = im_num - num[k] * math.sin(k * Om)
            re_den = re_den + den[k] * math.cos(k * Om)
            im_den = im_den - den[k] * math.sin(k * Om)

        mag_num = math.sqrt(re_num ** 2 + im_num ** 2)
        mag_den = math.sqrt(re_den ** 2 + im_den ** 2)
        magnitudes.append(mag_num / mag_den)
    return magnitudes


def espectro(x, frecuencias, fs):
    x = np.array(x)
    n = np.arange(len(x))            
    magnitudes = []
    for f in frecuencias:                
        Om = 2 * math.pi * f / fs
        re = np.sum(x * np.cos(n * Om))   
        im = -np.sum(x * np.sin(n * Om))   
        magnitudes.append(math.sqrt(re ** 2 + im ** 2))
    return magnitudes


if __name__ == "__main__":
    from diseno import disenar_filtro
    num, den = disenar_filtro(1000, 3500, 44100)
    print("y(n) =", filtrar([1, -1, 2], num, den))
    print("||H|| en fc1 y fc2 =", respuesta_frecuencia(num, den, [1000, 3500], 44100))