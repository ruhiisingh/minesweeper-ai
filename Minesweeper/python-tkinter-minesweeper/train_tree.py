from pathlib import Path
import numpy as np
import joblib

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def main():
    BASE_DIRECTORY = Path(__file__).resolve().parent
    INFO_PATH = BASE_DIRECTORY / "training_data.npz"
    MODEL_PATH = BASE_DIRECTORY / "minesweeper_tree.joblib"

    info = np.load(str(INFO_PATH))

    X = info["X"]
    Y = info["Y"]

    print("Training EX:", len(X))
    print("Features count:", X.shape[1])

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 42, stratify = Y)

    model = DecisionTreeClassifier(max_depth = 12, class_weight = "balanced", random_state = 42)

    model.fit(X_train, Y_train)

    predictions = model.predict(X_test)

    print(classification_report(Y_test, predictions, target_names = ["Safe", "Mine"], zero_division =0))

    joblib.dump(model,str(MODEL_PATH))

    print("Model saved to:", MODEL_PATH)

if __name__ == "__main__":
    main()


