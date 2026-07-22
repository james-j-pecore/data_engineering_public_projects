import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# X must be two-dimensional:
# 4 observations and 1 feature
X = np.array([[1], [2], [3], [4]])
y = np.array([3, 5, 7, 9])

model = LinearRegression()
model.fit(X, y)

predictions = model.predict(X)

print("Intercept:", model.intercept_)
print("Coefficient:", model.coef_[0])
print("Prediction for x=5:", model.predict([[5]])[0])
print("MSE:", mean_squared_error(y, predictions))
print("R²:", r2_score(y, predictions))