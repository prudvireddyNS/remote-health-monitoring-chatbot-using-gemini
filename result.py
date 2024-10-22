
from sklearn.model_selection import train_test_split
import pandas as pd
# Build the model with Random Forest Regressor :
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error
import lime
import lime.lime_tabular
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('data2.csv')
X = df['symptoms']
y = df['patient_id']
vectorizer = CountVectorizer()
X_vectorized = vectorizer.fit_transform(X)




X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size = 0.3, random_state = 0)
model = RandomForestRegressor(max_depth=6, random_state=0, n_estimators=10)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
# Load the data
mse = mean_squared_error(y_test, y_pred)**(0.5)
print("Mean Squared Error = ",mse)

X_train_dense = X_train.toarray()  # or X_train.todense()
explainer = lime.lime_tabular.LimeTabularExplainer(
    training_data=X_train_dense,  # Use the dense training data
    feature_names=X_train.columns if hasattr(X_train, 'columns') else [f'feature_{i}' for i in range(X_train_dense.shape[1])],
    mode='regression'  # Set mode to 'regression'
)
j=5
# For a specific instance you want to explain
instance = X_test[0].toarray()  # Convert the specific instance to dense format
instance = instance.flatten()  # Flatten to convert it to a 1D array

# Call explain_instance with the predict method for regression
exp = explainer.explain_instance(instance, model.predict, num_features=6)

# Optionally, display the explanation
# exp.show_in_notebook(show_table=True)  # or exp.as_pyplot_figure() if you're using matplotlib
# fig = exp.as_pyplot_figure()
# plt.show()
feature_importances = exp.as_list()

# Print the feature importances
for feature, importance in feature_importances:
    print(f"{feature}: {importance}")
