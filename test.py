import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

np.random.seed(42)
N = 800
X = np.random.randint(4, 10, size=(N, 15))
peer_mean = X[:, 5:15].mean(axis=1)
peer_std = X[:, 5:15].std(axis=1)

y = (
    0.25 * X[:, 0] +
    0.20 * X[:, 1] +
    0.10 * X[:, 2] +
    0.15 * X[:, 3] +
    0.10 * X[:, 4] +
    0.15 * peer_mean +
    -0.05 * peer_std +
    np.random.normal(0, 0.25, N)
)

df = pd.DataFrame(X)
df["peer_mean"] = peer_mean
df["peer_std"] = peer_std
df["FinalExam"] = y
df.columns = df.columns.astype(str)

features = df.drop("FinalExam", axis=1)
target = df["FinalExam"]

X_train, X_test, y_train, y_test = train_test_split(
    features, target, test_size=0.2, random_state=42
)

model = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    random_state=42
)

model.fit(X_train, y_train)
pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, pred))
