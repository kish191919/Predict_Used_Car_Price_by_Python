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
        global ml
        ml = pickle.load(f)

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

def actual_car_info():
    with open("./models/actual_car_info.plk","rb") as t:
        global actual_car_info
        actual_car_info = pickle.load(t)

init()
columns()
target_list()
actual_car_info()

@app.route("/")
def index():
    return render_template("index.html")



# API
@app.route("/predict/" , methods=["POST"])
def predict():
    target = pd.DataFrame(columns = columns)

    brand = request.values.get("brand")
    model = request.values.get("model")
    year = request.values.get("year")
    miles = request.values.get("miles")

    brand = str(brand)
    model = str(model)
    year = int(year)
    miles = int(miles)

    cdx = 0
    for col in columns:
        if col == 'brand'+"_"+brand:
            break;
        cdx += 1

    sdx = 0
    for col in columns:
        if col == 'model'+"_"+model:
            break;
        sdx += 1

    target_list[cdx] = 1
    target_list[sdx] = 1
    target_list[0] = year
    target_list[1] = miles

    for i in range(1):
        target.loc[i] = target_list

    numerical_features = ['year', 'miles']
    target[numerical_features] = np.log1p(target[numerical_features])
    price_log = ml.predict(target)
    price = np.exp(price_log)
    price = int(price)

    same_model = actual_car_info[actual_car_info["model"]==model]
    year_price = same_model[["year", "price"]]
    year_price_list = year_price.groupby("year").agg({'price':np.mean}).astype('int')
    year_price_list = year_price_list.reset_index()
    year_price_list["year"] = year_price_list["year"].apply(lambda x: str(x) )
    year_price_list["price"] = year_price_list["price"].apply(lambda x: str(x) )
    year_list = year_price_list["year"]
    price_list = year_price_list["price"]


    result = {"status": 200, "price":price, "year_list": list(year_list), "price_list":list(price_list)}
    print(result)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)







# $ gunicorn --reload dss:app
