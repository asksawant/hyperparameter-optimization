from calendar import SATURDAY
from functools import partial
from pyexpat import model
from turtle import pd
import pandas as pd
import numpy as np
import optuna

from sklearn import ensemble
from sklearn import metrics
from sklearn import model_selection

def optimize(trial, x, y):

    criterion = trial.suggest_categorical("criterion",["gini","entropy"])
    n_estimators = trial.suggest_int("n_estimators",100,1500)
    max_depth = trial.suggest_int("max_depth",3,15)
    max_features = trial.suggest_uniform("max_features",0.01,1.0)

    model = ensemble.RandomForestClassifier(
        criterion=criterion,
        n_estimators=n_estimators,
        max_depth=max_depth,
        max_features=max_features,
    )

    kf = model_selection.StratifiedKFold(n_splits=5)
    accuracies = []
    for idx in kf.split(X=x, y=y):
        train_idx, test_idx = idx[0], idx[1]
        xtrain = x[train_idx]
        ytrain = y[train_idx]

        xtest = x[test_idx]
        ytest = y[test_idx]

        model.fit(xtrain,ytrain)
        preds = model.predict(xtest)
        fold_acc = metrics.accuracy_score(ytest, preds)
        accuracies.append(fold_acc)
    return -1.0 * np.mean(accuracies)

if __name__ == "__main__":

    # reading the training dataset
    df = pd.read_csv("input/mobile_price_clf/train.csv")

    # features are all columns without price_range
    # note that there is no id column in this dataset
    # here we have training features
    X = df.drop("price_range", axis=1).values
    
    # Selecting the target
    y = df.price_range.values

    # creating partial function
    optimization_function = partial(optimize,x=X,y=y)

    study = optuna.create_study(direction="minimize")
    study.optimize(optimization_function, n_trials = 15)