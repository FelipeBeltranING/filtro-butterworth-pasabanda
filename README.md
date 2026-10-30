# Filtro Butterworth pasabanda

Filtro digital Butterworth pasabanda de orden 2 diseñado con la transformación bilineal y aplicado a voz capturada por micrófono.

## Características
- Diseño del filtro implementado desde cero: prewarping, transformación pasabanda y transformación bilineal.
- Filtrado mediante la ecuación en diferencias (IIR).
- Interfaz gráfica para ingresar los parámetros, grabar la voz y reproducir la señal original y la filtrada.
- Gráficas de la respuesta en frecuencia del filtro y de los espectros de entrada y salida, con la banda de paso y las bandas de rechazo marcadas.
- Visualización paso a paso del diseño matemático y de la ecuación en diferencias resultante.

## Estructura
| Archivo | Contenido |
|---|---|
| `diseno.py` | Diseño del filtro: prewarping, transformación pasabanda, transformación bilineal y coeficientes |
| `filtrado.py` | Ecuación en diferencias, respuesta en frecuencia ‖H(Ω)‖ y espectro ‖X(Ω)‖ |
| `main.py` | Interfaz gráfica (tkinter), micrófono, reproducción y gráficas |

## Parámetros por defecto
| Parámetro | Valor |
|---|---|
| Frecuencia de muestreo | 44100 Hz |
| Frecuencia de corte inferior | 1000 Hz |
| Frecuencia de corte superior | 3500 Hz |
| Ancho de banda | 2500 Hz |

## Instalación
```bash
pip install -r requirements.txt
```

## Uso
```bash
python main.py
```

Para ver solo los valores del diseño en consola:
```bash
python diseno.py
python filtrado.py
```