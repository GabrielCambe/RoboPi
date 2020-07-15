import pandas as pd
from load_dataset import load_dataset, load_dataset_dist, filter_minus1
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
import pickle
import sys


def loadRegressor(filename):
    loaded_model = pickle.load(open(filename, 'rb'))
    return load_model

def saveRegressor(model, filename):
    pickle.dump(model, open(filename, 'wb'), protocol=0)


if __name__ == "__main__":

    #dfSintetico = pd.read_csv("base-sintetica.csv")
    #print(dfSintetico.columns)
    #print(dfSintetico.describe)

    baseSinteticaSimples = load_dataset("./base-sintetica-semNomes.csv")
    baseSinteticaComplexa = load_dataset("./base2-sintetica-semNomes.csv")

    BSSx, BSSy = filter_minus1(baseSinteticaSimples)
    BSSx_train, BSSx_test, BSSy_train, BSSy_test = train_test_split(BSSx, BSSy, test_size=.25, shuffle=True, random_state=42)

    
    BSCx, BSCy = filter_minus1(baseSinteticaComplexa)
    BSCx_train, BSCx_test, BSCy_train, BSCy_test = train_test_split(BSCx, BSCy, test_size=.25, shuffle=True, random_state=42)
    
    randForstBSS = RandomForestRegressor()

    randForstBSC = RandomForestRegressor()

    randForstBSS.fit(BSSx_train, BSSy_train)
    randForstBSC.fit(BSCx_train, BSCy_train)

    BSS_score = randForstBSS.score(BSSx_test, BSSy_test)
    print(BSS_score)
    if(BSS_score > 0.85):
        randForstBSS.fit(BSSx, BSSy)
        saveRegressor(randForstBSS, 'randForstBSS.pickle')

    BSC_score = randForstBSC.score(BSCx_test, BSCy_test)
    print(BSC_score)
    if(BSC_score > 0.85):
        randForstBSC.fit(BSCx, BSCy)
        saveRegressor(randForstBSC, 'randForstBSC.pickle')
