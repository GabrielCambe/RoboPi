from load_dataset import load_dataset, load_dataset_dist, filter_minus1
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
import pickle
import sys
    
def loadRegressor(filename):
    loaded_model = pickle.load(open(filename, 'rb'))
    return load_model

def saveRegressor(model, filename):
    pickle.dump(model, open(filename, 'wb'))


if __name__ == "__main__":
    try:
        dataset = load_dataset(sys.argv[1])
    
        dataX, dataY = filter_minus1(dataset)
        X_train, X_test, Y_train, Y_test = train_test_split(dataX, dataY, test_size=.25, shuffle=True, random_state=42)
    
        regressorLinear = LinearRegression()
        regressorMLP = MLPRegressor(hidden_layer_sizes=(100, ), activation='relu', solver='lbfgs', alpha=0.0001, batch_size='auto', learning_rate='constant', learning_rate_init=0.001, power_t=0.5, max_iter=2000, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, n_iter_no_change=10)

        regressorLinear.fit(X_train, Y_train)
        regressorMLP.fit(X_train, Y_train)
        
        print(regressorLinear.score(X_test, Y_test))
        print(regressorMLP.score(X_test, Y_test))

        saveRegressor(regressorLinear, 'regressor_linear.pickle')
        saveRegressor(regressorMLP, 'regressor_mlp.pickle')

    except NameError:
        print("NameError! Cheque a definicao das suas variaveis ou passe o arquivo csv como argumento de entrada!")
