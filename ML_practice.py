#!/usr/bin/env python3

import os
import psycopg
import numpy as np          # good library for numerical operations (e.g., arrays)
import matplotlib.pyplot as plt    # standard scientific plotting library (e.g., think ggplot)
import pandas as pd                # for python dataframes + tidyverse analog  
import csv
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score


# Grab SQL connection details (hostname, dbname, username, and pwd) from local environment.


host = os.getenv("PGHOST", "localhost")
dbname = os.getenv("PGDATABASE")
user = os.getenv("PGUSER")
print(os.getenv("PGPASSWORD"))


conn = psycopg.connect(
    host=os.getenv("PGHOST", "localhost"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD")
)


query = """
SELECT * FROM slcs_abd_mtda
"""

query2 = """
SELECT * FROM slcs_abd
INNER JOIN (
    SELECT siteID,
    sitename,
    Cat_Elev,
    Cat_Aridity,
    Cat_pH,
    Cat_EC,
    Cat_clay,
    Cat_NO3,
    Cat_N,
    Cat_P,
    Cat_CN,
    Cat_C,
    Cat_D2C,
    Cat_Aspect
    FROM metadata
) AS m
ON m.siteID=slcs_abd.id_sample;
"""
print(query)    

df = pd.read_sql(query, conn)

print(df)
#quit()

#Pivot wide form to short form data
X = df.pivot_table(
    index="site_id",
    columns="taxon",
    values="abundance",
    fill_value=0
)

y = df.groupby("site_id")["moisture_class"].first()

print(X.shape)
print(X.head())

print(y)

# CLR-transform data

# Create Train / test dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train Random Forests on training dataset
# Create the model
model = RandomForestClassifier(random_state=42)
#model.fit(X_train, y_train)

# 3. Cross-validation ONLY on the training data
cv_scores = cross_val_score(
    model,
    X_train,
    y_train,
    cv=5,
    scoring="accuracy"
)

print("CV scores:", cv_scores)
print("Mean CV accuracy:", cv_scores.mean())

# Test training
#predictions = model.predict(X_test)




# Metrics (How well did it predict?)
    # accuracy (simplest metric)
from sklearn.metrics import accuracy_score
accuracy = accuracy_score(y_test, predictions)
print(accuracy) # accuracy is measured as an overall percentage

# confusion matrix
from sklearn.metrics import confusion_matrix   
cm = confusion_matrix(y_test, predictions)
print(cm) # prints a matrix showing exactly how many of each category were correctly and incorrectly assigned

# Feature importance: "What is the model using?"
# a random forest can estimate how useful (influential?) each featur was for making its decisions
importance = model.feature_importances_

feature_importance = pd.DataFrame({
    "taxon": X_train.columns,
    "importance": importance
})

feature_importance = feature_importance.sort_values(
    "importance",
    ascending=False
)

print(feature_importance)

# NOTE: feature importance does not equal biological causation

# Cross validation
