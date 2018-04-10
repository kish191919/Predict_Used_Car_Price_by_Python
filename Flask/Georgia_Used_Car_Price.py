from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd


app = Flask(__name__)
app.config.update(
    TEMPLATES_AUTO_RELOAD = True,
)
# model
# model = model.fit(X_train1, y_train1)
def init():
    with open("./models/model.plk","rb") as f:
        global model
        model = pickle.load(f)

# Train 데이터의 컬럼이름들 (dummy 컬럼 + 숫자 컬럼 이름)
# columns = pd.DataFrame(columns = [X_train1.columns])
def columns():
    with open("./models/column.plk","rb") as c:
        global columns
        columns = pickle.load(c)

# target_list = np.zeros_like(X_train.loc[0])
def target_list():
    with open("./models/target_list.plk","rb") as t:
        global target_list
        target_list = pickle.load(t)

init()
columns()
target_list()

@app.route("/")
def index():
    return render_template("index.html")


# API
@app.route("/predict/")
def predict():

    target = pd.DataFrame(columns = columns)

    company = request.values.get("company")
    subname = request.values.get("subname")
    year = request.values.get("year")
    mile = request.values.get("mile")
    # company = request.args.get("company")
    # subname = request.args.get("subname")
    # year = request.args.get("year")
    # mile = request.args.get("mile")

    # company = request.form["company"]
    # subname = request.form["subname"]
    # year =  request.form["year"]
    # mile = request.form["mile"]

    company = str(company)
    subname = str(subname)
    year = int(year)
    mile = int(mile)

    cdx = 0
    for col in columns:
        if col == 'company'+"_"+company:
            break;
        cdx += 1

    sdx = 0
    for col in columns:
        if col == 'subname'+"_"+subname:
            break;
        sdx += 1

    target_list[cdx] = 1
    target_list[sdx] = 1
    target_list[0] = year
    target_list[1] = mile

    for i in range(1):
        target.loc[i] = target_list

    numerical_features = ['year', 'mile']
    target[numerical_features] = np.log1p(target[numerical_features])
    price_log = model.predict(target)
    price = np.exp(price_log)
    price = int(price)
    result = {"status": 200, "result":price}

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)







# $ gunicorn --reload dss:app
