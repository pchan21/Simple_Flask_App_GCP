import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date
from sklearn.model_selection import train_test_split
import pickle

today = date.today()

def delete_digital_letter(word):
  new_word = ''
  for letter in word:
    if letter.isdigit() == False:
      new_word += letter
  return new_word.strip()

def delete_useless_word(word, list_element_to_delete_beginning_color):
  for useless_word in list_element_to_delete_beginning_color:
    if word.find(useless_word) != -1:
      word = word.replace(useless_word, '')
  for key, value in dict_color.items():
    if word.find(key) > -1:
      word = word.replace(key, value)
  return word.strip()

# On récupère les paramètres dont on a besoin
nber_annunces_per_page = 16
i= 1
# On récupère la bonne page
page_list_annunces = requests.get('https://www.lacentrale.fr/listing?makesModelsCommercialNames=PEUGEOT&options=&page=1').content
soup_page = BeautifulSoup(page_list_annunces, "html.parser")
tot_nber_ads = soup_page.find_all("h2", {"class":"titleNbAds"})[0]
tot_nber_ads = tot_nber_ads.find_all('span', {"class":"numAnn"})[0].get_text().replace('\xa0','')
nber_web_page = round(int(tot_nber_ads) / nber_annunces_per_page) + 1
nber_web_page = 100
list_name_car_in_url = ['PEUGEOT','RENAULT','VOLKSWAGEN','MERCEDES', 'CITROEN']
# éléments à supprimer
list_element_to_delete_beginning_color = ['p. m.', 'p.','peinture', 'd ', "d'", "teinte", 'to ', 'toit ', 'de ', 
                                          'gne ', 'nnp', 'kng', '+', '/', 'etoile/', '-']

dict_color = {'0mm00n6l': "bleu eclipse", 'n.c.': 'non codifie'}
# Pour RENAULT On a les données de PEUGEOT à supprimer
list_column_integer = ['Prix', 	'Dpt', 'Année','Kilométrage compteur', "Crit'Air",'Nombre de portes','Nombre de places','Garantie']
list_encoding = ['Marque voiture','Contrôle technique','Énergie','Boîte de vitesse', 'Garantie constructeur', 'Vérifié & Garanti','Première main (déclaratif)', 'Norme Euro','Couleur principale']

Dataframe_Global = pd.DataFrame()

for name_car in list_name_car_in_url:
  #data = pd.read_csv(f'Data_Site_Centrale/Data_{name_car}_{today}.csv')
  data = pd.read_csv(f'Data_Site_Centrale/Data_{name_car}_{today}.csv')
  Dataframe_Global = pd.concat([Dataframe_Global, data], axis=0)

Dataframe_Global['Couleur extérieure'] = Dataframe_Global['Couleur extérieure'].str.lower()
Dataframe_Global['Couleur extérieure'] = Dataframe_Global['Couleur extérieure'].apply(lambda x: delete_digital_letter(x))
Dataframe_Global['Couleur extérieure']  = Dataframe_Global['Couleur extérieure'].apply(lambda x: delete_useless_word(x, list_element_to_delete_beginning_color))
Dataframe_Global['Couleur principale'] = Dataframe_Global['Couleur extérieure'].apply(lambda x: x[:x.find(' ')] if x.find(' ') > -1 else x)
# On elève les éléments numériques
Dataframe_Global['Couleur principale'].value_counts()[50:100]
# On supprime ceux qui sont à l'unité
dict_color_keep = Dataframe_Global['Couleur principale'].value_counts()[Dataframe_Global['Couleur principale'].value_counts() > 1]
Dataframe_Global_filter_color = Dataframe_Global[Dataframe_Global['Couleur principale'].isin(list(dict_color_keep.keys()))]
Dataframe_Global_filter_color['Couleur Secondaire'] = Dataframe_Global_filter_color['Couleur extérieure'].apply(lambda x: x[x.find(' '):].strip() if x.find(' ') > -1 else x)
Dataframe_Global_filter_color['Couleur Secondaire'] = Dataframe_Global_filter_color['Couleur Secondaire'].apply(lambda x: x[:x.find(' ')].strip() if x.find(' ') > -1 else x)
# element to delete for Couleur Secondaire, remplace par la couleur principale
Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color['Couleur Secondaire'] == 'm','Couleur Secondaire'] = 'metallic'
Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color['Couleur Secondaire'] == 'f','Couleur Secondaire'] = 'foncé'
Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color['Couleur Secondaire'] == 'c','Couleur Secondaire'] = 'clair'
Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color['Couleur Secondaire'].isin(['(n)', '(nacré)', '(nacre)', 'nacrée']),'Couleur Secondaire'] = 'nacré'
Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color['Couleur Secondaire'] == 'gr','Couleur Secondaire'] = 'gris'
Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color['Couleur Secondaire'].isin(['to', 'toit']) ,'Couleur Secondaire'] = 'noir'
Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color['Couleur Secondaire'] == 'pur,','Couleur Secondaire'] = 'pur'
# Colonne pour les couleurs principales puis couleur pour les nuances 
# On définit les couleurs principales et on regarde si l'une des couleurs est présente pour les éléments les moins prépondérants au pire des cas


Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color['Garantie'].isna(), 'Garantie'] = 0
Dataframe_Global_filter_color['Garantie'] = Dataframe_Global_filter_color['Garantie'].str.replace('mois', '').str.strip()

# On enlève les voitures qui ont un nombre de places vide
Dataframe_Global_filter_color = Dataframe_Global_filter_color[~Dataframe_Global_filter_color["Nombre de places"].isna()]

Dataframe_Global_filter_color = Dataframe_Global_filter_color[(~Dataframe_Global_filter_color['Puissance fiscale'].isna()) 
                                                              & (~Dataframe_Global_filter_color['Puissance din'].isna()) 
                                                              & (~Dataframe_Global_filter_color["Crit'Air"].isna()) 
                                                              & (~Dataframe_Global_filter_color['Émissions de CO2'].isna())  
                                                              & (~Dataframe_Global_filter_color['Consommation mixte'].isna())
                                                              & (~Dataframe_Global_filter_color['Norme Euro'].isna())]

Dataframe_Global_filter_color['Puissance fiscale'] = Dataframe_Global_filter_color['Puissance fiscale'].apply(lambda x: int(x[:x.find('CV')].strip()))
Dataframe_Global_filter_color['Puissance din'] = Dataframe_Global_filter_color['Puissance din'].apply(lambda x: int(x[:x.find('ch')].strip()))
Dataframe_Global_filter_color['Émissions de CO2'] = Dataframe_Global_filter_color['Émissions de CO2'].apply(lambda x: int(x[:x.find('g/')].strip()))
Dataframe_Global_filter_color['Consommation mixte'] = Dataframe_Global_filter_color['Consommation mixte'].apply(lambda x: float(x[:x.find('l/')].strip()))

# On remplit avec les données logiquement
Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color["Garantie constructeur"].isna(), 'Garantie constructeur'] = 'Non'
Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color["Nombre de propriétaires"].isna(), 'Nombre de propriétaires'] = 1

Dataframe_Global_filter_color['Kilométrage compteur'] = Dataframe_Global_filter_color['Kilométrage compteur'].apply(lambda x: x.replace('Km','').replace(' ','').strip())
Dataframe_Global_filter_color['Marque voiture'] = Dataframe_Global_filter_color['Modèle'].apply(lambda x: x[:x.find(' ')].strip())
Dataframe_Global_filter_color['Modèle'] = Dataframe_Global_filter_color['Modèle'].apply(lambda x: x[x.find(' '):].strip())
Dataframe_Global_filter_color =  Dataframe_Global_filter_color.drop(['Modèle','Mise en circulation', 'Couleur extérieure', 'Moteur'], axis=1)
Dataframe_Global_filter_color['Garantite'] = Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color['Garantie'].isna(),'Garantie'] = 0

for column in list_column_integer:
  print(column)
  Dataframe_Global_filter_color[column] = Dataframe_Global_filter_color[column].apply(lambda x: int(x))

Dataframe_Global_filter_color.loc[~Dataframe_Global_filter_color['Vérifié & Garanti'].isna(), 'Vérifié & Garanti'] = 'oui'
Dataframe_Global_filter_color.loc[Dataframe_Global_filter_color['Vérifié & Garanti'].isna(), 'Vérifié & Garanti'] = 'non'

data = Dataframe_Global_filter_color.copy()
# column ='Boîte de vitesse'

# from sklearn.preprocessing import OneHotEncoder

# #creating instance of one-hot-encoder
# encoder = OneHotEncoder(handle_unknown='ignore')

# #perform one-hot encoding on 'team' column 
# encoder_df = pd.DataFrame(encoder.fit_transform(data[[column]]).toarray())

# #merge one-hot encoded columns back with original DataFrame
# final_df = data.join(encoder_df)

dict_values_encoding = {}

for value_encoding in list_encoding:
  dict_values_encoding[value_encoding] = list(Dataframe_Global_filter_color[value_encoding].unique())

# On enregistre nos valeurs associées au colonnes possédant des valeurs spécifiques
pickle.dump(dict_values_encoding, open('Values_Input/dict_specific_values.pickle', 'wb'))

liste_entree = ['Dpt', 'Année', 'Kilométrage compteur',
       'Nombre de portes', 'Nombre de places',
       'Nombre de propriétaires', 'Puissance fiscale', 'Puissance din',
       "Crit'Air", 'Émissions de CO2', 'Consommation mixte', 'Garantie', 'Marque voiture','Contrôle technique','Énergie','Boîte de vitesse', 'Garantie constructeur','Vérifié & Garanti', 'Première main (déclaratif)',
       'Norme Euro','Couleur principale']

pickle.dump(liste_entree, open('Entrees/list_input.pickle', 'wb'))
pickle.dump(list_encoding, open('Entrees/list_input_encoding.pickle', 'wb'))

data = pd.get_dummies(data, columns = list_encoding)
data = data.drop(['Couleur Secondaire'], axis=1)

X = data.drop(['Prix'], axis=1)
y = data[['Prix']]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train.to_csv(f'Data/X_train_{today}.csv')
X_test.to_csv(f'Data/X_test_{today}.csv')
y_train.to_csv(f'Data/y_train_{today}.csv')
y_test.to_csv(f'Data/y_test_{today}.csv')
