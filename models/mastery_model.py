import numpy as np
from sklearn.linear_model import LogisticRegression


class MasteryModel:
    """Small demo ML model that estimates probability of mastering a topic."""

    def __init__(self):
        self.model = LogisticRegression()
        self.model.fit(
            np.array([[0.2, 0], [0.4, 0], [0.6, 1], [0.8, 1], [1.0, 1]]),
            np.array([0, 0, 0, 1, 1]),
        )

    def predict(self, accuracy, attempts):
        x = np.array([[float(accuracy), int(attempts > 3)]])
        return round(float(self.model.predict_proba(x)[0][1]), 2)
