# Filtro Butterworth pasabanda

Filtro digital Butterworth pasabanda de orden 2 diseñado con la transformación bilineal y aplicado a audio capturado por micrófono en tiempo real.

## Características
- Diseño del filtro implementado desde cero: prewarping, transformación pasabanda y transformación bilineal.
- Filtrado mediante la ecuación en diferencias (IIR).
- Captura de voz desde el micrófono.
- Comparación del espectro de la señal original y la filtrada.
- Reproducción de ambas señales.

## Parámetros
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