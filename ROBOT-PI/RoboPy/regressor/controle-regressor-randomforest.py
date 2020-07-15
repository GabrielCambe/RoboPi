import pandas as pd
from load_dataset import load_dataset, load_dataset_dist, filter_minus1
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle
import sys


def loadRegressor(filename):
    loaded_model = pickle.load(open(filename, 'rb'))
    return load_model

def saveRegressor(model, filename):
    pickle.dump(model, open(filename, 'wb'))


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
    
    randForstBSS = RandomForestRegressor(n_estimators=100, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=0, warm_start=False, ccp_alpha=0.0, max_samples=None)

    randForstBSC = RandomForestRegressor(n_estimators=100, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=0, warm_start=False, ccp_alpha=0.0, max_samples=None)

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
