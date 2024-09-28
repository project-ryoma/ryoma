import math
from typing import Any, Dict, List, Tuple

import numpy as np


# calculate the entropy of the vector, avoid the case of 0 * log(0)
def calculate_entropy(probabilities: np.array) -> float:
    return -np.nansum(probabilities * np.log2(probabilities))


# calculate the entropy of the vector of list, avoid the case of 0 * log(0), not using numpy
def calculate_entropy_list(probs: list[float]) -> float:
    return -sum(pro * math.log2(pro) for pro in probs if pro > 0)


def test_calculate_entropy():
    probs = [0.5, 0.5]
    assert calculate_entropy(np.array(probs)) == calculate_entropy_list(probs)
    probs = [0.1, 0.9]
    assert calculate_entropy(np.array(probs)) == calculate_entropy_list(probs)
    probs = [0.9, 0.1]
    assert calculate_entropy(np.array(probs)) == calculate_entropy_list(probs)


def find_best_split(
    data: np.ndarray, labels: np.array, feature_idx: int
) -> tuple[float, float]:
    # get the unique values of the feature
    unique_values = np.unique(data[:, feature_idx])
    best_entropy = math.inf
    best_split_value = math.inf

    # iterate over the unique values and find the best split value
    for value in unique_values:
        left_indices, right_indices = split_datasets(data, value, feature_idx)
        left_labels = labels[left_indices]
        right_labels = labels[right_indices]

        left_entropy = calculate_entropy(
            np.array(
                [
                    np.sum(left_labels == label) / len(left_labels)
                    for label in np.unique(labels)
                ]
            )
        )
        right_entropy = calculate_entropy(
            np.array(
                [
                    np.sum(right_labels == label) / len(right_labels)
                    for label in np.unique(labels)
                ]
            )
        )

        total_entropy = left_entropy + right_entropy
        if total_entropy < best_entropy:
            best_entropy = total_entropy
            best_split_value = value

    return best_entropy, best_split_value


def test_find_best_split():
    data = np.array(
        [
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
            [4, 5, 6, 7, 8],
            [5, 6, 7, 8, 9],
        ]
    )
    labels = np.array([0, 1, 0, 1, 0])
    best_entropy, best_split_value = find_best_split(data, labels, 0)
    expected_entropy = 0.97
    # assert best_entropy and expected_entropy are close in 0.01
    assert abs(best_entropy - expected_entropy) < 0.01


# get the splitted datasets by the best split value
def split_datasets(
    data: np.ndarray, split_value: float, feature_idx: int
) -> list[np.ndarray]:
    max_threshold = data[:, feature_idx] < split_value
    left_indices = np.where(max_threshold)
    right_indices = np.where(~max_threshold)
    return [left_indices, right_indices]


# result be like:
# res = {
#   'feature_0_split_0': {
#       'feature_1_split_0': {
#         'feature_2_split_0': {
#
#         },
#         'feature_2_split_1': {
#
#         },
#       },
#       'feature_1_split_1': {
#
#       },
#   },
#   'feature_0_split_1': {
#   }
# }


class Node:
    def __init__(self):
        self.is_leaf = False
        self.left = None
        self.right = None
        self.split_value = None
        self.data = None


def build_tree(data, labels, feature):
    node = Node()
    if feature == 2:
        node.is_leaf = True
        node.data = data
    else:
        _, split_value = find_best_split(data, labels, feature)
        left_indices, right_indices = split_datasets(data, split_value, feature)
        node.left = build_tree(data[left_indices], labels[left_indices], feature + 1)
        node.right = build_tree(data[right_indices], labels[right_indices], feature + 1)
        node.split_value = split_value
    return node


def test_build_tree():
    data = np.array(
        [
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [1, 4, 5, 6, 7],
            [4, 5, 6, 7, 8],
            [1, 6, 7, 8, 9],
        ]
    )

    labels = np.array([0, 1, 0, 1, 0])

    root = build_tree(data, labels, 0)

    assert root.split_value == 2
    print(root.left)


# def get_result_levelwise(data, labels, feature):
#     if feature == 2:
#         return data
#     else:
#         res = {}
#         _, split_value = find_best_split(data, labels, feature)
#         left_indices, right_indices = split_datasets(data, split_value, feature)

#         res['feature_{}_split_0'.format(feature)] = get_result_levelwise(
#             data[left_indices], labels, feature + 1
#         )
#         res['feature_{}_split_1'.format(feature)] = get_result_levelwise(
#             data[right_indices], labels, feature + 1
#         )
#         return res
