import pandas as pd
import numpy as np


def load_data(url="https://archive.ics.uci.edu/ml/machine-learning-databases/voting-records/house-votes-84.data"):
    """
    Loads the Congressional Voting Records dataset from a given URL.

    Parameters:
        url (str): URL to the dataset.

    Returns:
        pd.DataFrame: Loaded dataset with column names assigned.
    """
    column_names = ["class",
                    "handicapped-infants",
                    "water-project",
                    "adoption-of-the-budget-resolution",
                    "physician-fee-freeze",
                    "el-salvador-aid",
                    "religious-groups-in-schools",
                    "anti-satellite-test-ban",
                    "aid-to-nicaraguan-contras",
                    "mx-missile",
                    "immigration",
                    "synfuels-corporation-cutback",
                    "education-spending",
                    "superfund-right-to-sue",
                    "crime",
                    "duty-free-exports",
                    "export-administration-act-south-africa"]
    df = pd.read_csv(url, names=column_names)
    return df


def handle_missing_values(df, mode=0):
    """
    Handles missing values ("?") in the dataset.

    Parameters:
        df (pd.DataFrame): The dataset.
        mode (int): 0 to treat "?" as a third valid category,
                    1 to replace "?" with the most frequent value (mode) for the attribute.

    Returns:
        pd.DataFrame: The processed dataset with handled missing values.
    """
    if mode == 0:
        # Leave "?" as a valid third category.
        return df
    else:
        # Replace "?" with the most frequent value in the column.
        for col in df.columns[1:]:
            mode_val = df.loc[df[col] != "?", col].mode()[0]
            df.loc[df[col] == "?", col] = mode_val
        return df


def stratified_split(df, test_size=0.2):
    """
    Splits the dataset into stratified training and test sets while maintaining class proportions.

    Parameters:
        df (pd.DataFrame): The dataset.
        test_size (float): Proportion of the dataset to include in the test split.

    Returns:
        tuple: Training and test datasets as pandas DataFrames.
    """
    df = df.sample(frac=1).reset_index(drop=True)  # Shuffle the data.
    class_counts = df['class'].value_counts()
    train_indices = []
    test_indices = []

    for c in class_counts.index:
        c_indices = df[df['class'] == c].index.tolist()
        split_point = int((1 - test_size) * len(c_indices))
        train_indices.extend(c_indices[:split_point])
        test_indices.extend(c_indices[split_point:])

    train_df = df.loc[train_indices].reset_index(drop=True)
    test_df = df.loc[test_indices].reset_index(drop=True)
    return train_df, test_df


class NaiveBayesClassifier:
    """
    A Naive Bayes Classifier implementation with Laplace smoothing.
    """

    def __init__(self, laplace_lambda=1.0):
        """
        Initializes the classifier with Laplace smoothing.

        Parameters:
            laplace_lambda (float): The smoothing parameter (default is 1.0).
        """
        self.laplace_lambda = laplace_lambda
        self.class_priors = {}
        self.feature_probs = {}
        self.classes_ = None
        self.features_ = None
        self.feature_values_ = {}

    def fit(self, X, y):
        """
        Fits the Naive Bayes model to the training data.

        Parameters:
            X (pd.DataFrame): Feature set.
            y (pd.Series): Target labels.
        """
        self.classes_ = y.unique()
        self.features_ = X.columns

        for f in self.features_:
            self.feature_values_[f] = X[f].unique()

        class_counts = y.value_counts()
        total = len(y)

        for c in self.classes_:
            self.class_priors[c] = class_counts[c] / total
            X_c = X[y == c]
            self.feature_probs[c] = {}

            for f in self.features_:
                self.feature_probs[c][f] = {}
                for val in self.feature_values_[f]:
                    count_val = (X_c[f] == val).sum()
                    numerator = count_val + self.laplace_lambda
                    denominator = len(X_c) + self.laplace_lambda * len(self.feature_values_[f])
                    self.feature_probs[c][f][val] = numerator / denominator

    def predict(self, X):
        """
        Predicts the class labels for the given data.

        Parameters:
            X (pd.DataFrame): The input feature set.

        Returns:
            list: Predicted class labels.
        """
        preds = []
        for i in range(len(X)):
            row = X.iloc[i]
            class_scores = {}

            for c in self.classes_:
                log_prob = np.log(self.class_priors[c])
                for f in self.features_:
                    val = row[f]
                    if val not in self.feature_probs[c][f]:
                        numerator = self.laplace_lambda
                        denominator = len(X) + self.laplace_lambda * len(self.feature_values_[f])
                        p = numerator / denominator
                    else:
                        p = self.feature_probs[c][f][val]
                    log_prob += np.log(p)
                class_scores[c] = log_prob

            preds.append(max(class_scores, key=class_scores.get))
        return preds

    def score(self, X, y):
        """
        Evaluates the model's accuracy on the given data.

        Parameters:
            X (pd.DataFrame): The feature set.
            y (pd.Series): The true labels.

        Returns:
            float: Accuracy score.
        """
        preds = self.predict(X)
        return (np.array(preds) == np.array(y)).mean()


def cross_validate(model, X, y, k=10):
    """
    Performs k-fold cross-validation on the given data.

    Parameters:
        model (NaiveBayesClassifier): The classifier.
        X (pd.DataFrame): Feature set.
        y (pd.Series): Target labels.
        k (int): Number of folds.

    Returns:
        list: Accuracy scores for each fold.
    """
    indices = np.arange(len(y))
    np.random.seed(42)
    np.random.shuffle(indices)
    fold_sizes = [len(y) // k + (1 if i < len(y) % k else 0) for i in range(k)]
    current = 0
    scores = []

    for fold_size in fold_sizes:
        test_idx = indices[current:current + fold_size]
        train_idx = np.concatenate([indices[:current], indices[current + fold_size:]])
        current += fold_size

        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]

        model_fold = NaiveBayesClassifier(laplace_lambda=model.laplace_lambda)
        model_fold.fit(X_train, y_train)
        acc = model_fold.score(X_test, y_test)
        scores.append(acc)
    return scores


def main():
    mode = int(input("Enter 0 to treat '?' as a third category or 1 to replace it with the mode: "))
    df = load_data()
    df = handle_missing_values(df, mode=mode)

    train_df, test_df = stratified_split(df, test_size=0.2)
    X_train, y_train = train_df.drop("class", axis=1), train_df["class"]
    X_test, y_test = test_df.drop("class", axis=1), test_df["class"]

    model = NaiveBayesClassifier(laplace_lambda=1.0)
    model.fit(X_train, y_train)

    train_acc = model.score(X_train, y_train)
    cv_scores = cross_validate(model, X_train, y_train, k=10)
    cv_mean, cv_std = np.mean(cv_scores), np.std(cv_scores)
    test_acc = model.score(X_test, y_test)

    print(f"1. Train Set Accuracy: {train_acc * 100:.2f}%")
    print("\n10-Fold Cross-Validation Results:")
    for i, score in enumerate(cv_scores, 1):
        print(f"  Fold {i}: {score * 100:.2f}%")
    print(f"\n  Average Accuracy: {cv_mean * 100:.2f}%")
    print(f"  Standard Deviation: {cv_std * 100:.2f}%")
    print(f"\n2. Test Set Accuracy: {test_acc * 100:.2f}%")


if __name__ == "__main__":
    main()
