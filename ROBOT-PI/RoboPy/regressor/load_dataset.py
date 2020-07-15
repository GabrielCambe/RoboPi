import numpy as np
import csv
import sys

def filter_minus1(dataset):
    dataX = dataset[0]
    dataY = dataset[1]
    filtered_dataX = []
    filtered_dataY = []
    for x,y in zip(dataX,dataY):
        if y == -1:
            pass
        else:
            filtered_dataX.append(x)
            filtered_dataY.append(y)
    return filtered_dataX, filtered_dataY
    

def load_dataset(filepath):
    with open(filepath,'r') as dest_f:
        data_points = []
        data_labels = []
        data_iter = csv.reader(dest_f, delimiter = ',', quotechar = '"')
        for data in data_iter:
            size = len(data)
            data_points.append(data[0:(size-1)])
            data_labels.append(data[(size-1)]) 
        data_points_array = np.asarray(data_points, dtype = float)
        data_labels_array = np.asarray(data_labels, dtype = float)
    return data_points_array, data_labels_array

def load_dataset_dist(filepath):
    with open(filepath,'r') as dest_f:
        data_points = []
        data_labels = []
        data_iter = csv.reader(dest_f, delimiter = ',', quotechar = '"')
        for data in data_iter:
            size = len(data)
            data_points.append(data[2:(size-1)])
            data_labels.append(data[(size-1)]) 
        data_points_array = np.asarray(data_points, dtype = float)
        data_labels_array = np.asarray(data_labels, dtype = float)
    return data_points_array, data_labels_array

if __name__ == "__main__":
    try:
        dataset = load_dataset(sys.argv[1])
        dataX, dataY = filter_minus1(dataset)
        
        print("DadosX:")
        print(dataX)
        print("DimensoesX:")
        try:
            print(len(dataX[0]))
        except TypeError:
            print(1)
            
        print("DadosY:")
        print(dataY)
        print("DimensoesY:")
        try:
            print(len(dataY[0]))
        except TypeError:
            print(1)
                
        print("Numero de pontos:")
        print(len(dataX))

    except NameError:
        print("Passe o nome do arquivo csv como argumento!")

