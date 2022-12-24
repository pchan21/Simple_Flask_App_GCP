import os
from flask import Flask
from flask import render_template
from datetime import date
from flask import request
import numpy as np
import pandas as pd
# à tester
import pickle
app= Flask(__name__)

dict_units_input = {'Émissions de CO2': 'g/km', 'Consommation mixte': 'l/100km', 'Puissance fiscale': 'CV', 'Puissance din':'cv','Garantie': 'mois'}

@app.route("/")
def hello_world():
    today = '2022-12-24'
    data_values_encoding = pickle.load(open(f'Values_Input/dict_specific_values.pickle','rb'))
    data_name_input = pickle.load(open(f'Entrees/list_input.pickle','rb'))
    data_name_encoding = pickle.load(open(f'Entrees/list_input_encoding.pickle','rb'))
    Dataframe = pd.read_csv(f'Data/X_train_{today}.csv', index_col=False)
    Dataframe = Dataframe.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1)
    score = round(float(pickle.load(open('Modele/best_model_score.txt', 'rb'))),2)
    return render_template('home.html', score=score, data_name_input=data_name_input,data_values_encoding=data_values_encoding,data_name_encoding=data_name_encoding, dict_units_input=dict_units_input)
	
	
@app.route('/predict',methods = ['POST'])
def predict():
    with open('Entrees/last_modele_date.txt') as f:
    	lines = f.readlines()
    today = lines[0]	
    data_values_encoding = pickle.load(open(f'Values_Input/dict_specific_values.pickle','rb'))
    data_name_input = pickle.load(open(f'Entrees/list_input.pickle','rb'))
    data_name_encoding = pickle.load(open(f'Entrees/list_input_encoding.pickle','rb'))
    Dataframe = pd.read_csv(f'Data/X_train_{today}.csv', index_col=False)
    Dataframe = Dataframe.drop(['Unnamed: 0.1','Unnamed: 0'], axis=1) #
    score = round(float(pickle.load(open('Modele/best_model_score.txt', 'rb'))),2)
    dict_input_values = {}
    # On parcourt les colonnes pour les avoir dans l'ordre
    for column in Dataframe.columns:
        if column in data_name_input:
            dict_input_values[column] = [request.form.get(column)]
        else:
            if column[:column.find('_')] + '_' + request.form.get(column[:column.find('_')]) == column:
                dict_input_values[column] = [1]
            else:
                dict_input_values[column] = [0]

    #x_predict = pd.DataFrame(data=dict_input_values)  
    #print(x_predict)
    filename = 'Modele/best_model.sav'
    #model = pickle.load(open(filename, 'rb'))
    #print(dict_input_values['Couleur principale_blanc'])
    #final_features = [np.array(int_features)]
    #prediction = model.predict(x_predict)
    #print(prediction[0])
    #prediction = [0.32]
    #print(model.predict(x_predict)[0][0])
    prediction = 0.32#round(model.predict(x_predict)[0][0],2)
    #print(prediction)
    #output = round(prediction[0], 2)
    if prediction < 0:
        answer = "La voiture n'est pas vendable au vue des paramètres rentrés"
    else:
        answer = f'La voiture coûtera {prediction} euros'
    return render_template('home.html', score=score,prediction_text=answer, data_values_encoding=data_values_encoding, data_name_input=data_name_input,data_name_encoding=data_name_encoding, dict_units_input=dict_units_input) # prediction[0]

    #int_features = [float(x) for x in request.form.values()]
    #final_features = [np.array(int_features)]
    #prediction = model.predict(final_features)
    #print(prediction[0])
    #prediction = [0.32]
    #output = round(prediction[0], 2)
    #return render_template('home.html', prediction_text="AQI for Jaipur {}".format(prediction[0])) # prediction[0]

if __name__=="__main__":
    app.run(debug=True)
    #app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT",8080)))
