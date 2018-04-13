
# coding: utf-8

# In[ ]:


import MySQLdb, pickle
import pandas as pd
from sqlalchemy import create_engine
from collections import Counter
import numpy as np
import pandas as pd

# read local car_info popular
pw = pickle.load(open('./models/pw.plk','rb'))

db = MySQLdb.connect(
    "13.125.22.6",
    "root",
    pw,
    "used_car",
    charset='utf8',
)

SQL_QUERY = """
    SELECT *
    FROM used_car;
"""

train = pd.read_sql(SQL_QUERY, db)

pickle.dump(train, open("./models/database.plk","wb"))

brand_list = []
for brand in Counter(train.brand).most_common(30):
    brand_list.append(brand[0])

idx_list = []
idx = 0
for i in train["brand"]:
    if i not in brand_list:
        idx_list.append(idx)
    idx += 1

train = train.drop(idx_list)
train.reset_index(drop=True, inplace=True)
train = train.drop("index", axis=1)


categorical_features = ['brand', 'model']

dummy_cat = pd.get_dummies(train[categorical_features])

numerical_features = ['year', 'miles','price']

normalize_num = np.log1p(train[numerical_features])

# pre_train = pd.merge(normalize_num, dummy_cat)
X_train_0 = normalize_num.join(dummy_cat)
y_train = X_train_0["price"]
X_train = X_train_0.drop("price", axis=1)

from xgboost import XGBRegressor
from sklearn.cross_validation import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

k_fold = KFold(n_splits=10, shuffle=True, random_state=2018)
X_train1, X_test1, y_train1, y_test1 = train_test_split(X_train, y_train)

ml = XGBRegressor(n_estimators=1000, learning_rate=0.05, verbose=False)

ml = ml.fit(X_train1, y_train1)
y_pred = ml.predict(X_test1)

pickle.dump(ml, open("./models/model.plk","wb"))

actual_car_info = train[["brand", "model","year","miles","price"]]
pickle.dump(actual_car_info, open("/models/actual_car_info.plk","wb"))

target = pd.DataFrame(columns = [X_train1.columns])

pickle.dump(X_train1.columns, open("./models/column.plk","wb"))

cdx = 0
for col in X_train.columns:
    if col == 'brand'+"_"+brand:
        break;
    cdx += 1

sdx = 0
for col in X_train.columns:
    if col == 'model'+"_"+model:
        break;
    sdx += 1

target_list = np.zeros_like(X_train.loc[0])

pickle.dump(target_list, open("./models/target_list.plk","wb"))

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

same_model = actual_car_info[actual_car_info["model"]==model]
year_price = same_model[["year", "price"]]
year_price_list = year_price.groupby("year").agg({'price':np.mean}).astype('int')
year_price_list = year_price_list.reset_index()

year_price_list["year"] = year_price_list["year"].apply(lambda x: str(x) )

year_price_list["price"] = year_price_list["price"].apply(lambda x: str(x) )

same_brand = actual_car_info["brand"].groupby()
