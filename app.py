from flask import Flask, render_template, request, url_for, redirect
import joblib
import datetime
import csv
from dateutil.parser import parse
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

app = Flask(__name__, template_folder='template')
#app = FastAPI()

def predict_model():
    data = pd.read_csv('Test_csv.csv')
    print(data["age_days"])
    data["bmi"] = data["weight"] / (data["height"] / 100) ** 2
    data['years'] = (data['age_year']).round().astype('int')
    standardScaler = StandardScaler()
    scale_columns = ['age_year', 'height', 'weight', 'ap_hi', 'ap_lo', 'bmi']
    data[scale_columns] = standardScaler.fit_transform(data[scale_columns])
    loaded_model = joblib.load('knnModel.pkl', mmap_mode ='r')
    prediction = loaded_model.predict_proba(data)
    predstr = np.array2string(prediction, precision=2, separator=',')
    prediction_final = float(predstr[2] + predstr[3] + predstr[4] + predstr[5])
    return prediction_final



def date_to_age(Bdate):
    today = datetime.datetime.now()
    date = today.strftime("%d-%m-%Y")
    date2 = date + (" 0:00:00")
    date_today = parse(date2)
    Bday = datetime.datetime.fromisoformat(Bdate)
    age_days = today - Bday
    return age_days.days

def write_to_csv(age_days,age_years,gender,height,weight,sbp,dbp,cholesterol,glucose,smoke,alcohol,active):
    f = open('Test_csv.csv', 'w')
    writer = csv.writer(f)
    header = ['age_days', 'age_year', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke',
              'alco', 'active']
    row = [age_days,age_years,gender,height,weight,sbp,dbp,cholesterol,glucose,smoke,alcohol,active]
    # write a row to the csv file
    writer.writerow(header)
    writer.writerow(row)


@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/', methods=['POST'])
def uploadFile():
    bdate = request.form['Birthdate']
    print (bdate)
    age_days = date_to_age(bdate)
    age_years = age_days / 365
    height = request.form['Height']
    weight = request.form['Weight']
    sbp = request.form['SBP']
    dbp = request.form['DBP']
    gender = request.form['Gender']
    cholesterol = request.form['Cholesterol']
    glucose = request.form['Glucose']
    smoke = request.form['Smoke']
    alcohol = request.form['Alcohol']
    active = request.form['Active']
    print (age_days,age_years,gender,height,weight,sbp,dbp,cholesterol,glucose,smoke,alcohol,active)
    write_to_csv(age_days,age_years,gender,height,weight,sbp,dbp,cholesterol,glucose,smoke,alcohol,active)
    return redirect(url_for('predict'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = predict_model()
    remark = ""
    if prediction > 85:
        remark = "Your score is high meaning that you have a low risk Cardiovascular Disease"
    elif prediction >70:
        remark= "Your score average. Quitting smoking and drinking of alcohol will help you to improve your score."
    elif prediction > 60:
        remark = "Your score is below average. You a moderate chance of getting cardiovascular disease. Quitting smoking and drinking of alcohol will help you to improve your score."
    else:
        remark= "Your score is dangerously low. You are at high risk of getting cardiovascular disease. It is adviced for you to see a cardiology specialists when possible."
    print (remark)
    return render_template('prediction.html', data=prediction, remark=remark)




if __name__ == "__main__":
    app.run()
