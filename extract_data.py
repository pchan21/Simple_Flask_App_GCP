from bs4 import BeautifulSoup
from datetime import date
import numpy as np
import pandas as pd
import requests
import time
import requests


today = date.today()
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
# Pour RENAULT On a les données de PEUGEOT à supprimer

# lancement à 17h30 du code
# On parcourt les pages web des annonces
# for car_mark in list_name_car_in_url:
for mark in list_name_car_in_url:
  list_rows_annunces = []
  for i in range (1,nber_web_page+1):
    time.sleep(1.5)
    # On récupère la bonne page
    response_annunces = requests.get(f'https://www.lacentrale.fr/listing?makesModelsCommercialNames={mark}&options=&page={i}&sortBy=firstOnlineDateDesc')
    page_list_annunces = response_annunces.content
    statuscodeannunces = response_annunces.status_code
    if statuscodeannunces == 200:
      soup_page = BeautifulSoup(page_list_annunces, "html.parser")
      # On parcourt les annonces puis..
      list_annunces = soup_page.find_all('div',{"class":"resultList mB15 hiddenOverflow listing"})[0]
      for annunces in list_annunces.find_all('div', {"class": "adLineContainer"}):
        json_row = {}
        if annunces.find_all('a') != []:
          a_beacon = annunces.find_all('a')[0]
          # On récupère le lien qui permet à la description de l'annonce
          link_to_car_description = a_beacon.get('href')
          # Bloc de description
          container_description = annunces.find_all('div', {"class":"searchCard__rightContainer"})[0]
          # Pour récupérer le nom du modèle de la voiture
          model_car_information = container_description.find_all('h3',{"class":"searchCard__makeModelTitle"})[0]
          json_row['Modèle'] = model_car_information.find_all('span', {"class": "searchCard__makeModel"})[0].get_text()
          json_row['Moteur'] = model_car_information.find_all('span', {"class": "searchCard__version"})[0].get_text()
          # Pour récupérer le prix de la voiture
          price_valuation = container_description.find_all("div",{"class":"searchCard__fieldPriceBadge-container"})[0]
          price_car = price_valuation.find_all('div', {"class":"searchCard__fieldPrice"})[0].get_text().replace('\xa0','').replace('€','')
          json_row['Prix'] = price_car 
          # Pour récupérer le département 
          dpt_valuation = container_description.find_all("div",{"class":"searchCard__customerLocalisation" })[0]
          dpt_car = dpt_valuation.find_all('div', {"class":"searchCard__dptCont"})[0].get_text()
          json_row['Dpt'] = dpt_car
          # Via le lien du href on récupère toutes les données importantes pour la vente
          time.sleep(1)
          if link_to_car_description[0] == '/':
            response = requests.get(f'https://www.lacentrale.fr{link_to_car_description}')
            page_automobile = response.content
            statuscode = response.status_code
          else:
            response = requests.get(f'https://www.lacentrale.fr/{link_to_car_description}')
            page_automobile = response.content
            statuscode = response.status_code
          if statuscode == 200:
            soup = BeautifulSoup(page_automobile, "html.parser")
            fictive_data_with_information = soup.find_all("div", {"class":"cbm-moduleInfos__informationList cbm-moduleInfos__information_column_break"})
            if fictive_data_with_information != []:
              fictive_data_with_information = fictive_data_with_information[0]
              # On récupère tous les éléments descriptifs des voitures pour nécessaire à l'évolution de son prix
              for ul_table in fictive_data_with_information.find_all('ul'):
                for criteria in ul_table.find_all('li'):
                  json_row[criteria.find_all('span')[0].get_text().replace(':','').replace('?','').strip()] = criteria.find_all('span')[1].get_text().replace(':','').strip()
              list_rows_annunces.append(json_row)
            else:
              fictive_data_with_information = soup.find_all("div", {"class":"cbm-moduleInfos__informationList"})[0]
              for ul_table in fictive_data_with_information.find_all('ul'):
                for criteria in ul_table.find_all('li'):
                  json_row[criteria.find_all('span')[0].get_text().replace(':','').replace('?','').strip()] = criteria.find_all('span')[1].get_text().replace(':','').strip()
              list_rows_annunces.append(json_row)
  Data_Bilan = pd.DataFrame(list_rows_annunces)
  Data_Bilan = Data_Bilan[['Modèle', 'Moteur', 'Prix', 'Dpt', 'Année', 'Mise en circulation',
          'Contrôle technique', 'Kilométrage compteur', 'Énergie',
          'Boîte de vitesse', 'Couleur extérieure', 'Nombre de portes',
          'Nombre de places', 'Garantie', 'Garantie constructeur',
          'Vérifié & Garanti', 'Première main (déclaratif)',
          'Nombre de propriétaires', 'Puissance fiscale', 'Puissance din',
          "Crit'Air", 'Émissions de CO2', 'Consommation mixte', 'Norme Euro']]
  Data_Bilan.to_csv(f'Data_Site_Centrale/Data_{mark}_{today}.csv')
  time.sleep(10)

