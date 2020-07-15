# ------------------------------------------------------------------
# Esse programa carrega um csv com os pontos de distancia 
# ------------------------------------------------------------------
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle
import sys
import pandas
import numpy as np
    
def loadRegressor(filename):
    loaded_model = pickle.load(open(filename, 'rb'))
    return loaded_model

def fit_score_save(features, labels, regressor, scoreThreshold, filename):    
    trainFeatures, testFeatures, trainLabels, testLabels = train_test_split(features, labels, test_size=.25, shuffle=True, random_state=42)
    regressor.fit(trainFeatures, trainLabels)
    score = regressor.score(testFeatures, testLabels)
    print(score)
    if(score > scoreThreshold):
        regressor.fit(features, labels)
        pickle.dump(regressor, open(filename+'.pickle', 'wb'), protocol=2)
    
if __name__ == "__main__":
    try:
        dataset = pandas.read_csv(sys.argv[1])
        labels = np.array(dataset['pwm'])
        features = np.array(dataset[['frontSensor', 'rightSensor', 'leftSensor']])
        regressorLinear = LinearRegression()
        regressorMLP = MLPRegressor(hidden_layer_sizes=(100, ), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='constant', learning_rate_init=0.001, power_t=0.5, max_iter=2000, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, n_iter_no_change=10)
        randForst = RandomForestRegressor(n_estimators=100, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=0, warm_start=False)

        
        fit_score_save(features, labels, regressorLinear, 0.85, 'linear')
        fit_score_save(features, labels, regressorMLP, 0.85, 'perceptron')
        fit_score_save(features, labels, randForst, 0.85, 'forest')

        for filename in ['linear.pickle', 'perceptron.pickle', 'forest.pickle']:
            try:
                loadtest = loadRegressor(filename)
                print(loadtest)
            except (NameError, FileNotFoundError, IOError) as error:
                print(error)
                print("NameError! Cheque a definicao das suas variaveis ou passe o arquivo csv como argumento de entrada!")
                
    except NameError:
        print("NameError! Cheque a definicao das suas variaveis ou passe o arquivo csv como argumento de entrada!")
