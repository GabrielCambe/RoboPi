#!/usr/bin/python
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle
import sys
import pandas
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "csv_file",
    help="The file containing the data.", type=str
)
parser.add_argument(
    "-s", "--score",
    nargs="?",
    dest="score_threshold",
    const=0.6, default=0.85,
    help="The score threshold percentage for the fitting.", type=float
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "--pwm",
    help="Set the labels as the pwm values of the motors.",
    action="store_true"
)
group.add_argument(
    "--control",
    help="Set the labels as the gamepad's Lx and Ly axis variables.",
    action="store_true"
)
parser.add_argument(
    "-e", "--encoder",
    dest="with_encoder",
    help="Use the encoder values as features of the model",
    action="store_true"
)
parser.add_argument(
    "-v", "--verbose",
    help="Print verbose information",
    action="store_true"
)


def loadRegressor(filename):
    loaded_model = pickle.load(open(filename, 'rb'))
    return loaded_model

def fit_score_save(features, labels, regressor, scoreThreshold, filename):    
    trainingFeatures, validatingFeatures, trainingLabels, validatingLabels = train_test_split(features, labels, test_size=.5, shuffle=True, random_state=42)
    trainFeatures, testFeatures, trainLabels, testLabels = train_test_split(trainingFeatures, trainingLabels, test_size=.25, shuffle=True, random_state=42)
    

    regressor.fit(trainFeatures, trainLabels)
    score = regressor.score(testFeatures, testLabels)
    print(score)
    
    if(score > scoreThreshold):
        regressor.fit(trainingFeatures, trainingLabels)
        score = regressor.score(validatingFeatures, validatingLabels)
        print(score)

        if(score > scoreThreshold):
            regressor.fit(features, labels)
            pickle.dump(regressor, open(filename+'.pickle', 'wb'), protocol=2)
    
    #print(regressor.predict([features[0]]))
    #print(regressor.predict([features[0]])[0][0])
    #print(regressor.predict([features[0]])[0][1])

def get_regressors(features, labels, score_threshold):            
    regressorLinear = LinearRegression()
    regressorMLP = MLPRegressor(hidden_layer_sizes=(100, ), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='constant', learning_rate_init=0.001, power_t=0.5, max_iter=2000, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, n_iter_no_change=10)
    randForst = RandomForestRegressor(n_estimators=100, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=0, warm_start=False)

    fit_score_save(features, labels, regressorLinear, score_threshold, 'linear')
    fit_score_save(features, labels, regressorMLP, score_threshold, 'perceptron')
    fit_score_save(features, labels, randForst, score_threshold, 'forest')

    for filename in ['linear.pickle', 'perceptron.pickle', 'forest.pickle']:
        try:
            loadtest = loadRegressor(filename)
            print(loadtest)
        except (NameError, IOError) as error:
            print(error)
            print("NameError! Cheque a definicao das suas variaveis ou passe o arquivo csv como argumento de entrada!")


if __name__ == "__main__":
    args = parser.parse_args()

    dataset = pandas.read_csv(args.csv_file)


    if args.with_encoder:
        features = np.array(dataset[['frontSensor', 'rightSensor', 'leftSensor', 'ticksRight', 'ticksLeft']])
    else:
        features = np.array(dataset[['frontSensor', 'rightSensor', 'leftSensor']])

 
    if args.pwm:
        labels = np.array(dataset['pwm'])
        get_regressors(features, labels, args.score_threshold)

    if args.control:    
        labels = np.array(dataset[['gamepadLx', 'gamepadLy']])
        get_regressors(features, labels, args.score_threshold)       
    



# elif(sys.argv[2] == 'all'):
#     print(dataset.tail(5))
#     mask = ~(dataset.columns.isin(['gamepadLx', 'gamepadLy']))
#     cols_to_shift = dataset.columns[mask]
    
#     dataset[cols_to_shift] = dataset[cols_to_shift].shift(-1)
#     print(dataset.tail(5))
    
#     dataset = dataset.dropna()
#     print(dataset.tail(5))
    
#     labels_dataset = dataset[['gamepadLx', 'gamepadLy']]
#     labels = np.array(labels_dataset)
#     features_dataset = dataset[['frontSensor', 'rightSensor', 'leftSensor', 'steerLeft', 'steerRight']]
#     features = np.array(features_dataset.dropna())
#     get_regressors(features, labels)
