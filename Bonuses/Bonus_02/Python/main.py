import pandas as pd
import math
from collections import Counter
from scipy.spatial import KDTree
import matplotlib.pyplot as plt

def load_and_preprocess_data():
    """
    Loads the Iris dataset and performs Min-Max normalization.

    Returns:
    --------
    data : pandas.DataFrame
        Normalized Iris dataset.
    """
    # Load the Iris dataset
    data = pd.read_csv('iris.data', header=None)
    data.columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'class']

    # Apply Min-Max normalization
    for feature in ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']:
        min_value = data[feature].min()
        max_value = data[feature].max()
        data[feature] = (data[feature] - min_value) / (max_value - min_value)

    return data

def stratified_train_test_split(data):
    """
    Splits the data into stratified training and testing sets.

    Parameters:
    -----------
    data : pandas.DataFrame
        The dataset to be split.

    Returns:
    --------
    train_data : pandas.DataFrame
        Training set (80% of the data).
    test_data : pandas.DataFrame
        Testing set (20% of the data).
    """
    # Shuffle the data
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)

    # Group data by class
    grouped_data = data.groupby('class')

    train_data = pd.DataFrame()
    test_data = pd.DataFrame()

    # Perform stratified splitting
    for class_name, group in grouped_data:
        train_size = int(0.8 * len(group))
        train_data = pd.concat([train_data, group.iloc[:train_size]], axis=0)
        test_data = pd.concat([test_data, group.iloc[train_size:]], axis=0)

    # Reset indices
    train_data = train_data.reset_index(drop=True)
    test_data = test_data.reset_index(drop=True)

    return train_data, test_data

def kNN_kd_tree(kd_tree, train_labels, test_instance_features, k):
    """
    Predicts the class of a test instance using kNN with a kd-tree.

    Parameters:
    -----------
    kd_tree : scipy.spatial.KDTree
        kd-tree built from the training data.
    train_labels : numpy.ndarray
        Labels of the training data.
    test_instance_features : numpy.ndarray
        Features of the test instance.
    k : int
        Number of nearest neighbors.

    Returns:
    --------
    predicted_class : str
        Predicted class label.
    """
    # Query the kd-tree for k nearest neighbors
    distances, indices = kd_tree.query(test_instance_features, k=k)
    # Ensure indices is a list
    if k == 1:
        indices = [indices]
    # Get the classes of the neighbors
    neighbor_labels = train_labels[indices]
    # Majority vote for the predicted class
    vote_counts = Counter(neighbor_labels)
    predicted_class = vote_counts.most_common(1)[0][0]
    return predicted_class

def calculate_accuracy_kd_tree(data_set, k, kd_tree, train_labels):
    """
    Computes the accuracy of the kNN classifier using kd-tree.

    Parameters:
    -----------
    data_set : pandas.DataFrame
        Dataset for evaluation.
    k : int
        Number of nearest neighbors.
    kd_tree : scipy.spatial.KDTree
        kd-tree built from the training data.
    train_labels : numpy.ndarray
        Labels of the training data.

    Returns:
    --------
    accuracy : float
        Accuracy in percentage.
    """
    correct_predictions = 0
    data_features = data_set.iloc[:, :-1].values
    data_labels = data_set['class'].values
    for idx in range(len(data_set)):
        test_instance_features = data_features[idx]
        actual_class = data_labels[idx]
        predicted_class = kNN_kd_tree(kd_tree, train_labels, test_instance_features, k)
        if actual_class == predicted_class:
            correct_predictions += 1
    accuracy = (correct_predictions / len(data_set)) * 100
    return accuracy

def cross_validation_kd_tree(train_data, k):
    """
    Performs 10-fold cross-validation using kNN and kd-tree.

    Parameters:
    -----------
    train_data : pandas.DataFrame
        Training dataset.
    k : int
        Number of nearest neighbors.

    Returns:
    --------
    average_accuracy : float
        Average accuracy over 10 folds.
    std_deviation : float
        Standard deviation of the accuracies.
    """
    # Shuffle the training data
    train_data = train_data.sample(frac=1, random_state=42).reset_index(drop=True)
    fold_size = int(len(train_data) / 10)
    accuracies = []

    for fold in range(10):
        start = fold * fold_size
        end = start + fold_size
        # Split into validation and training sets
        validation_set = train_data.iloc[start:end].reset_index(drop=True)
        training_set = pd.concat([train_data.iloc[:start], train_data.iloc[end:]], axis=0).reset_index(drop=True)
        # Build kd-tree
        training_features = training_set.iloc[:, :-1].values
        training_labels = training_set['class'].values
        kd_tree = KDTree(training_features)
        # Calculate accuracy
        accuracy = calculate_accuracy_kd_tree(validation_set, k, kd_tree, training_labels)
        accuracies.append(accuracy)
        print(f"    Accuracy Fold {fold + 1}: {accuracy:.2f}%")

    average_accuracy = sum(accuracies) / len(accuracies)
    variance = sum((x - average_accuracy) ** 2 for x in accuracies) / len(accuracies)
    std_deviation = math.sqrt(variance)
    print(f"\n    Average Accuracy: {average_accuracy:.2f}%")
    print(f"    Standard Deviation: {std_deviation:.2f}%")
    return average_accuracy, std_deviation

def plot_accuracy_vs_k(train_data, test_data, max_k=25):
    """
    Plots accuracy vs k for k values from 1 to max_k (odd numbers only).

    Parameters:
    -----------
    train_data : pandas.DataFrame
        Training dataset.
    test_data : pandas.DataFrame
        Testing dataset.
    max_k : int, optional
        Maximum value of k (default is 25).
    """
    ks = list(range(1, max_k + 1, 2))
    train_accuracies = []
    test_accuracies = []

    # Build kd-tree with training data
    train_features = train_data.iloc[:, :-1].values
    train_labels = train_data['class'].values
    kd_tree = KDTree(train_features)

    for k in ks:
        # Compute accuracy on training set
        train_accuracy = calculate_accuracy_kd_tree(train_data, k, kd_tree, train_labels)
        train_accuracies.append(train_accuracy)
        # Compute accuracy on test set
        test_accuracy = calculate_accuracy_kd_tree(test_data, k, kd_tree, train_labels)
        test_accuracies.append(test_accuracy)

    plt.figure(figsize=(10, 6))
    plt.plot(ks, train_accuracies, label='Training Accuracy', marker='o')
    plt.plot(ks, test_accuracies, label='Testing Accuracy', marker='s')
    plt.xlabel('k')
    plt.ylabel('Accuracy (%)')
    plt.title('Accuracy vs k')
    plt.legend()
    plt.grid(True)
    plt.xticks(ks)
    plt.show()

def main():
    """
    Main function to execute the kNN algorithm with kd-tree and display results.
    """
    # Load and preprocess the dataset
    data = load_and_preprocess_data()

    # Split the data into training and testing sets
    train_data, test_data = stratified_train_test_split(data)

    # Get the value of k from the user
    k = int(input("Enter the value of k: "))

    # Build kd-tree with training data
    train_features = train_data.iloc[:, :-1].values
    train_labels = train_data['class'].values
    kd_tree = KDTree(train_features)

    # 1. Train Set Accuracy
    train_accuracy = calculate_accuracy_kd_tree(train_data, k, kd_tree, train_labels)
    print("\n1. Train Set Accuracy:")
    print(f"    Accuracy: {train_accuracy:.2f}%")

    # 2. 10-Fold Cross-Validation
    print("\n2. 10-Fold Cross-Validation Results:")
    cross_validation_kd_tree(train_data, k)

    # 3. Test Set Accuracy
    test_accuracy = calculate_accuracy_kd_tree(test_data, k, kd_tree, train_labels)
    print("\n3. Test Set Accuracy:")
    print(f"    Accuracy: {test_accuracy:.2f}%")

    # Bonus: Plot Accuracy vs k
    plot_choice = input("\nWould you like to see the accuracy vs k graph? (yes/no): ")
    if plot_choice.lower() == 'yes':
        plot_accuracy_vs_k(train_data, test_data)

if __name__ == "__main__":
    main()
