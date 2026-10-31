import math


def disenar_filtro(fc1, fc2, fs):
    a = math.tan(math.pi * fc1 / fs)
    b = math.tan(math.pi * fc2 / fs)

    B = b - a         
    W = a * b          

    A = math.sqrt(2) * B          
    C = 2 * W + B ** 2            
    D = math.sqrt(2) * B * W      
    E = W ** 2                    

    n0 = B ** 2
    n2 = -2 * B ** 2
    n4 = B ** 2

    d0 = 1 + A + C + D + E
    d1 = -4 - 2 * A + 2 * D + 4 * E
    d2 = 6 - 2 * C + 6 * E
    d3 = -4 + 2 * A - 2 * D + 4 * E
    d4 = 1 - A + C - D + E

    num = [n0 / d0, 0.0, n2 / d0, 0.0, n4 / d0]          
    den = [1.0, d1 / d0, d2 / d0, d3 / d0, d4 / d0]     

    return num, den


if __name__ == "__main__":
    num, den = disenar_filtro(1000, 3500, 44100)
    print("Coeficientes del numerador   b0..b4:", num)
    print("Coeficientes del denominador a0..a4:", den)