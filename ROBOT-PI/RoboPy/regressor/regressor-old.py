from load_dataset import load_dataset, filter_minus1
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle
import sys
    
def loadRegressor(filename):
    loaded_model = pickle.load(open(filename, 'rb'))
    return loaded_model

def saveRegressor(model, filename):
    pickle.dump(model, open(filename, 'wb'))


if __name__ == "__main__":
    try:
        dataset = load_dataset_dist(sys.argv[1])
    except:
        print("Passe o nome do arquivo csv como argumento!")
        
    dataX, dataY = filter_minus1(dataset)
    X_train, X_test, Y_train, Y_test = train_test_split(dataX, dataY, test_size=.25, shuffle=True, random_state=42)

    regressor = LinearRegression()
    regressor.fit(X_train, Y_train)
    print(regressor.score(X_test, Y_test))
    
