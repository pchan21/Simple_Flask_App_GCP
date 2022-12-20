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

@app.route("/")
def hello_world():
    data_values_encoding = pickle.load(open(f'Values_Input/dict_specific_values.pickle','rb'))
    data_name_input = pickle.load(open(f'Entrees/list_input.pickle','rb'))
    data_name_encoding = pickle.load(open(f'Entrees/list_input_encoding.pickle','rb'))
    Dataframe = pd.read_csv('Data/X_train.csv', index_col=False)
    Dataframe = Dataframe.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1)
    return render_template('home.html', data_values_encoding=data_values_encoding, data_name_input=data_name_input,data_name_encoding=data_name_encoding)
	
	
@app.route('/predict',methods = ['POST'])
def predict():
    #int_features = [float(x) for x in request.form.values()]
    #final_features = [np.array(int_features)]
    #prediction = model.predict(final_features)
    #print(prediction[0])
    prediction = [0.32]
    #output = round(prediction[0], 2)
    return render_template('home.html', prediction_text="AQI for Jaipur {}".format(prediction[0])) # prediction[0]

if __name__=="__main__":
    app.run(debug=True)
    #app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT",8080)))
