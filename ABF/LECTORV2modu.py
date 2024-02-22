import tkinter as tk
from tkinter import filedialog
import pyabf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
# Lectura de archivo
def read_file():
    # Crea una instancia de la clase Tk
    root = tk.Tk()
    # Oculta la ventana principal
    root.withdraw()
    # Abre una ventana de selección de archivo
    file_path = filedialog.askopenfilename()
    # Imprime el path del archivo seleccionado
    abf = pyabf.ABF(file_path)
    # Imprimir información sobre el archivo
    print("Informacion del archivo ABF:")
    print(f"Nombre del archivo: {abf.abfID}")
    print(f"Duracion del experimento: {abf.sweepLengthSec} segundos")
    print(f"Frecuencia de muestreo: {abf.dataRate} Hz")
    print(f'Numero de canales: {abf.channelCount}')
    print(f"Numero de sweeps: {abf.sweepCount}")
    # Destruye la instancia de la clase Tk
    root.destroy()
    return abf
# Seccionar grafica
def section_plots(ax, abf_name, canal):
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    fig.subplots_adjust(wspace=0.2)

    for i, axi in enumerate(axs):
        if i < ax.lines.get_size() and ax.lines is not None:
            inicio = i * 200
            final = min((i + 1) * 200, len(ax.lines[i].get_ydata()))
            axi.plot(ax.lines[i].get_xdata()[inicio:final], ax.lines[i].get_ydata()[inicio:final], transform=ax.transData)
            axi.set_xticks([])
            axi.set_yticks([])

            if i == 0:
                axi.set_ylabel(f'Canal {canal+1}')
            if i == 0:
                axi.set_xlabel('time (s)')
        else:
            axi.set_axis_off()

    fig.savefig(f'{abf_name}_canal_{canal+1}.jpg', bbox_inches='tight', dpi=300)
    plt.close(fig)
# Procesamiento de datos
def abf_process(abf):
    if abf.sweepCount > 0:
        # Obtenemos dimensiones de los datos
        dimensiones = abf.sweepY
        print('Dimensiones Datos: ',dimensiones.shape)
        # Obtener datos del tiempo solo para corroborar
        time = np.transpose(abf.sweepX)
        np.transpose(time)
        print('Dimensiones time: ',time.shape)
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
            axs[i].set_xlabel("time (s)")
            axs[i].set_ylabel("Datos de la señal")
            axs[i].legend()
        fig.tight_layout()
        plt.show()
        for canal in range(abf.channelCount):
            section_plots(axs[canal], abf.abfID, canal)
    else:
        print("No hay sweeps en el archivo ABF.")
        
def main():
    abf_process(read_file())

if __name__ == '__main__':
    main()