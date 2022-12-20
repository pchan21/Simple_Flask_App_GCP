from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression
import pandas as pd
from datetime import date
import pickle


today = date.today()
#loaded_model = pickle.load(open(filename, 'rb'))

X_train = pd.read_csv('Data/X_train.csv')
X_test = pd.read_csv('Data/X_test.csv')
y_train = pd.read_csv('Data/y_train.csv')
y_test = pd.read_csv('Data/y_test.csv')

y_train = y_train.drop(['Unnamed: 0'], axis=1)
X_train = X_train.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1)
y_test = y_test.drop(['Unnamed: 0'], axis=1)
X_test = X_test.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1)

# Test_linear Regresion
lr = LinearRegression()
lr.fit(X_train, y_train)

score_lr = lr.score(X_test,y_test)

neigh = KNeighborsRegressor(n_neighbors=2)
neigh.fit(X_train, y_train)

score_neigh = neigh.score(X_test, y_test)

if score_lr > score_neigh:
    pickle.dump(lr, open(f'Modele/best_model_{today}.sav', 'wb'))
    pickle.dump(score_lr, open(f'Modele/best_model_score_{today}.txt', 'wb'))
if score_neigh > score_lr:
    pickle.dump(neigh, open(f'Modele/best_model_{today}.sav', 'wb'))
    pickle.dump(score_neigh, open(f'Modele/best_model_score_{today}.txt', 'wb'))