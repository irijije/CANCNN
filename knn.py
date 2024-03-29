import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support as score

from config import Config



Config.NAME = "DoS"
#Config.NAME = "Fuzzy"
#Config.NAME = "gear"
#Config.NAME = "RPM"

Config.FILENAME = f"dataset/{Config.NAME}_dataset.csv"


def test():
    df = pd.read_csv(Config.FILENAME, names=[str(x) for x in range(12)], header=None)
    df = df[['0', '1', '11']]
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    df['1'] = df['1'].apply(int, base=16)
    #df[['3', '4', '5', '6', '7', '8', '9', '10']] = df[['3', '4', '5', '6', '7', '8', '9', '10']].applymap(lambda x: int(x, 16))
    df['11'] = df['11'].apply(lambda x: 1 if x == 'T' else 0)
    
    Y = df.pop('11')
    X = df

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 100)

    n = 20
    clf = KNeighborsClassifier(n_neighbors=n)
    clf.fit(X_train, Y_train)

    Y_ = clf.predict(X_test)
    acc = clf.score(X_test, Y_test)*100

    precision, recall, _, _ = score(Y_test, Y_, zero_division=1)

    print(f'{Config.NAME} knn {n} {acc} {precision} {recall}')


if __name__ == "__main__":
    test()