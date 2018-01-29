import numpy as np
import pandas
from datetime import datetime as dt
from sklearn import svm
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA as pca
import data_prepration as data_prep
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler


# TRAIN_FEATURE_FILE_NAME = '../data/results/features_just_data.csv'
# TEST_FEATURE_FILE_NAME = '../data/results/test_just_data.csv'

# nu is An upper bound on the fraction of training errors and
# a lower bound of the fraction of support vectors.
# Should be in the interval (0, 1]. By default 0.5 will be taken.

# kernel is rbf

# gamma is Kernel coefficient for 'rbf', 'poly' and 'sigmoid'.
# If gamma is 'auto' then 1/n_features will be used instead.

class OneClassSVMModel(object):
    def __init__(
            self,
            raw_train_file_name,
            col_names,
            nu_parameter,
            gamma_parameter,
            scale_method
    ):
        self.raw_train_file_name = raw_train_file_name
        self.col_names = col_names
        self.nu_parameter = nu_parameter
        self.gamma_parameter = gamma_parameter
        self.scale_method = scale_method
        self.minmax_scale = MinMaxScaler(feature_range=(0, 1))
        self.standard_scale = StandardScaler(with_mean=0, with_std=1)

        # train the scalers
        raw_data = data_prep.get_data_frame_values(raw_train_file_name, col_names)
        self.minmax_scale.fit(raw_data)
        self.standard_scale.fit(raw_data)

        # load and scale the training data
        if scale_method == ScaleMethod.Normalize:
            self.scaled_train_data = self.minmax_scale.transform(raw_data)
        else:
            self.scaled_train_data == self.standard_scale.transform(raw_data)

        # fit the model
        self.clf = svm.OneClassSVM(nu=nu_parameter, kernel="rbf", gamma=gamma_parameter, verbose=True)
        self.clf.fit(self.scaled_train_data)

    def get_scale_method(self):
        return self.scale_method

    def get_minmax_scaler(self):
        return self.minmax_scale

    def get_standard_scaler(self):
        return self.standard_scale

    def get_scaled_dataset(self):
        return self.scaled_train_data

    def get_feature_names(self):
        return self.col_names

    def get_nu_parameter(self):
        return self.nu_parameter

    def set_nu_parameter(self, nu):
        self.nu_parameter = nu

    def get_gamma_parameter(self):
        return self.gamma_parameter

    def set_gamma_parameter(self, gamma):
        self.gamma_parameter = gamma

    def get_predictions(self, scaled_samples):
        # NOTE: samples should be scaled with the same scaling method that applied to the training dataset
        # Predict if a particular sample is an outlier or not.
        # Tells whether or not (+1 or -1) each sample should be considered as an inlier according to the fitted model.
        return self.clf.predict(scaled_samples)

    def get_num_errors(self, y_pred):
        return y_pred[y_pred == -1].size

    def is_outlier(self, new_data):
        # Reshape your data either using X.reshape(-1, 1) if your data has a single feature or
        # X.reshape(1, -1) if it contains a single sample.
        # The anomaly score of the input samples. The lower, the more abnormal
        scaled_data = None
        if self.scale_method == ScaleMethod.Normalize:
            scaled_data = self.minmax_scale.transform(np.array(new_data).reshape(1, -1))
        else:
            scaled_data = self.standard_scale.transform(np.array(new_data).reshape(1, -1))
        return self.clf.decision_function(scaled_data)

    def plot_data(self, samples, fig_name):
        # plot training data
        # pca
        # fit the normalized dataset to a pca object, and reduce dimensions from 16 to 2
        fig = plt.figure()
        normalized_samples = data_prep.normalize_data(samples, self.col_names)
        y_pred_samples = self.get_predictions(data_prep.get_scaled_data(samples, self.col_names, self.scale_method))
        pca_obj = pca(n_components=2)
        pca_transformed = pandas.DataFrame(pca_obj.fit_transform(normalized_samples))
        plt.scatter(pca_transformed[y_pred_samples == -1][0], pca_transformed[y_pred_samples == -1][1], label='Outlier',
                    c='red')
        plt.scatter(pca_transformed[y_pred_samples == 1][0], pca_transformed[y_pred_samples == 1][1], label='Inlier',
                    c='blue')
        ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
        plt.legend(loc=2)
        plt.title('PCA Plot of %d Samples\n kernel = RBF nu = %s gamma = %s\nDimension reduction from %d to 2'
                  % (len(y_pred_samples), str(self.nu_parameter), str(self.gamma_parameter), len(self.col_names)))
        plt.savefig('../data/diagrams/%s_%s.png' % (fig_name, ts), bbox_inches='tight')


# plot
from metadata import attribute_names
from data_prepration import ScaleMethod

one_svm = OneClassSVMModel('../data/results/features_just_data.csv',
                           attribute_names.FEATURE_NAMES,
                           0.1,
                           0.1,
                           ScaleMethod.Normalize)
# one_svm.plot_data('../data/results/features_just_data.csv', 'train_data_plot_svm')
new_data = [10, 5.0, 0.033, 0.143, 0.125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.4, 11.429, 4.382, 4.667, 0.395]
print one_svm.is_outlier(new_data)
