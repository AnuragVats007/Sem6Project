from typing import Tuple, Union, List
import numpy as np
from sklearn.linear_model import *
from sklearn import preprocessing as pr
from sklearn import model_selection as ms
import openml
import pandas as pd

XY = Tuple[np.ndarray, np.ndarray]
Dataset = Tuple[XY, XY]
LogRegParams = Union[XY, Tuple[np.ndarray]]
XYList = List[XY]


def get_model_parameters(model: LogisticRegression) -> LogRegParams:
    """Returns the paramters of a sklearn LogisticRegression model."""
    if model.fit_intercept:
        params = [
            model.coef_,
            model.intercept_,
        ]
    else:
        params = [
            model.coef_,
        ]
    return params


def set_model_params(
    model: LogisticRegression, params: LogRegParams
) -> LogisticRegression:
    """Sets the parameters of a sklean LogisticRegression model."""
    model.coef_ = params[0]
    if model.fit_intercept:
        model.intercept_ = params[1]
    return model


def set_initial_params(model: LogisticRegression):
    """Sets initial parameters as zeros Required since model params are
    uninitialized until model.fit is called.

    But server asks for initial parameters from clients at launch. Refer
    to sklearn.linear_model.LogisticRegression documentation for more
    information.
    """
    n_classes = 2  # MNIST has 10 classes
    n_features = 3 # Number of features in dataset
    model.classes_ = np.array([i for i in range(2)])

    model.coef_ = np.zeros((n_classes, n_features))
    if model.fit_intercept:
        model.intercept_ = np.zeros((n_classes,))


# def load_mnist() -> Dataset:
#     """Loads the MNIST dataset using OpenML.

#     OpenML dataset link: https://www.openml.org/d/554
#     """
#     mnist_openml = openml.datasets.get_dataset(61)
#     Xy, _, _, _ = mnist_openml.get_data(dataset_format="array")
#     X = Xy[:, :-1]  # the last column contains labels
#     y = Xy[:, -1]
#     # First 60000 samples consist of the train set
#     x_train, y_train = X[:60000], y[:60000]
#     x_test, y_test = X[60000:], y[60000:]
#     return (x_train, y_train), (x_test, y_test)

def load_mnist() -> Dataset:
    df = pd.read_csv('medical_data.csv')
    # removing ID
    df = df.drop('ID',axis=1)
    # removing null values
    df = df.dropna()

    x=df.iloc[:,:-1]
    y=df.iloc[:,-1:]

    std = pr.StandardScaler()
    x_std = std.fit_transform(x)

    le = pr.LabelEncoder()
    y_le = le.fit_transform(y.values)
    x_train,x_test,y_train,y_test = ms.train_test_split(x_std,y_le,test_size=0.3,random_state=(42))
    
    return (x_train, y_train), (x_test, y_test)


def shuffle(X: np.ndarray, y: np.ndarray) -> XY:
    """Shuffle X and y."""
    rng = np.random.default_rng()
    idx = rng.permutation(len(X))
    return X[idx], y[idx]


def partition(X: np.ndarray, y: np.ndarray, num_partitions: int) -> XYList:
    """Split X and y into a number of partitions."""
    return list(
        zip(np.array_split(X, num_partitions), np.array_split(y, num_partitions))
    )
