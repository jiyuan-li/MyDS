import pandas as pd
import numpy as np
import warnings


class InfoGain:

    def __init__(self, X, y, **params):
        """
        :param X: training data X
        :param y: training data y (single target)
        :split mode: the way of splitting data, supports "random", "medium"
        """
        self._train_X = X
        self._train_y = y
        self._split_threshold = self.get_split_threshold(params)
        self._target_entropy = self.cal_target_entropy(self._train_y)

    def get_random_split_threshold(self):
        """Generate random split threshold for all cols

        :return: a dictionary of random split threshold for all cols
        """
        split_threshold_dict = {}
        for col in self._train_X:
            split_threshold_dict[col] = self._train_X[col].sample(n=1).iloc[0]

        return split_threshold_dict

    def get_split_threshold(self, params):
        """

        :param params: params to split data, one can specify split_mode = "random" or specify the split_threshold
        manually. the split_threshold is defined as a dictionary, for example, "split_threshold":{"var1":1, "var2":2}
        :return: a dictionary contains split threshold for each variable
        """
        try:
            split_mode = params["split_mode"]
            if split_mode == "random":
                split_threshold = self.get_random_split_thredshold()
            else:
                warnings.warn("split mode [%s] not supported yet" % split_mode)
        except KeyError:
            try:
                split_threshold = params["split_threshold"]
            except KeyError:
                warnings.warn("If split_mode is not given, then split_threshold has to be specified")
                exit(-1)

        return split_threshold

    @staticmethod
    def entropy(prob_list):
        """

        :param prob_list: a list contains the probability of all classes
        :return: the entropy
        """
        result = 0
        for prob in prob_list:
            result -= prob * np.log2(prob)
        return result

    def cal_target_entropy(self, df_target):
        """
        :return: the entropy of the target column
        """
        class_prob = df_target.value_counts() / df_target.shape[0]
        target_entropy = self.entropy(list(class_prob.values))

        return target_entropy

    def calc_variable_entropy(self, col):
        """calculate the entropy of column col
        :param col: column that the entropy is calculated for
        """
        positive_index = self._train_X[self._train_X[col] >= self._split_threshold[col]].index
        negative_index = self._train_X.index.difference(positive_index)

        target_entropy_positive = self.cal_target_entropy(self._train_y.iloc[positive_index])
        target_entropy_negative = self.cal_target_entropy(self._train_y.iloc[negative_index])

        p_positive = len(positive_index) / len(self._train_X.index)
        variable_entropy = p_positive * target_entropy_positive + (1 - p_positive) * target_entropy_negative
        return variable_entropy

    def cal_info_gain(self):
        """calculate information gain for each column

        :return: a dictionary of information gain
        """
        info_gain_dict = {}
        for col in self._train_X:
            info_gain_dict[col] = self._target_entropy - self.calc_variable_entropy(col)

        return info_gain_dict

