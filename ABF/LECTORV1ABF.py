import pyabf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# Ruta al archivo ABF
ruta_archivo_abf = 'ABF/15n24009.abf'

# Cargar el archivo ABF
abf = pyabf.ABF(ruta_archivo_abf)

# Imprimir información sobre el archivo
print("Informacion del archivo ABF:")
print(f"Nombre del archivo: {abf.abfID}")
print(f"Duracion del experimento: {abf.sweepLengthSec} segundos")
print(f"Frecuencia de muestreo: {abf.dataRate} Hz")
print(f'Numero de canales: {abf.channelCount}')
print(f"Numero de sweeps: {abf.sweepCount}")
print('holamundo')
#Comprobamos que haya más de un dato para poder trabajar
if abf.sweepCount > 0:
    # Obtenemos dimensiones de los datos
    dimensiones = abf.sweepY
    print('Dimensiones Datos: ',dimensiones.shape)
    # Obtener datos del tiempo solo para corroborar
    tiempo = np.transpose(abf.sweepX)
    np.transpose(tiempo)
    print('Dimensiones tiempo: ',tiempo.shape)
    # Definimos una matriz para poder ingresarla a un DataFrame
    abf.setSweep(sweepNumber=0,channel=2)
    dataMatrix = np.array([abf.sweepY])
    dataMatrix = np.transpose(dataMatrix)
    # DataFrame con pandas
    df = pd.DataFrame(dataMatrix, columns = ['Datos'])
    # Eliminamos los datos de los primeros 4 segundos
    df = df.drop(df.index[:4000])
    # Encontramos el valor mas pequeño del DataFrame
    min_value = df.min().min() # Definimos valor minimo para calcular umbral
    print(f'Min Value: {min_value}')
    #Calculamos el umbral
    threshold = min_value + 2 * df['Datos'].std()
    print(threshold)
    #Deteccion de incidencias
    start_indices = []
    end_indices = []
    current_state = 'below'
    for i , value in enumerate(df['Datos']):
        if value > threshold and current_state == 'below':
            start_indices.append(i)
            current_state = 'above'
        elif value < threshold and current_state == 'above':
            end_indices.append(i)
            current_state = 'below'
    #Detección de picos
    bells = []
    for start, end in zip(start_indices,end_indices):
        bells.append(df['Datos'].iloc[start:end])
        # print(bells)
    #Impresion de datos de cada pico
    bell_stats = np.zeros((len(bells),4))
    for i,bell in enumerate(bells):
        print(f'\nPico #{i+1}\n')
        #Realizamos calculos y asignamos valores
        media = bell.mean()
        temp_array = np.nan_to_num(bell, nan=np.nanmean(media))
        desviación_estandar = np.std(temp_array)
        min = bell.min().min()
        max = bell.max().max()
        # Llenado de datos
        bell_stats[i] = [media,desviación_estandar,min,max]
        #Impresion de calculos
        print(f'\nMedia: {media}')
        print(f'Desviación estandar : {desviación_estandar}')
        print(f'Minimos: {min} \n Maximos: {max}')
        print('\n---------------------------------')
    #Creamos dataFrame para los calculos
        stats_df= pd.DataFrame(data=bell_stats,columns=['Media','Desviación_Estandar','Minimo','Maximo'])
        print(stats_df)
    # Graficamos cada canal para obtener la informacion en graficas independientes
    fig, axs = plt.subplots(abf.channelCount,1,figsize=(10,6))
    for i in range(abf.channelCount):
        abf.setSweep(sweepNumber=0,channel=i)
        axs[i].plot(abf.sweepX, abf.sweepY, label=f'Canal {i+1}')
        axs[i].set_title(f"Datos del canal {i+1} durante el experimento")
        axs[i].set_xlabel("Tiempo (s)")
        axs[i].set_ylabel("Datos de la señal")
        axs[i].legend()
    fig.tight_layout()
    plt.show()
else:
    print("No hay sweeps en el archivo ABF.")