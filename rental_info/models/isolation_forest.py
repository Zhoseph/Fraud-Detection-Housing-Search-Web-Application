import numpy as np
import pandas
from datetime import datetime as dt
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA as pca
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.externals import joblib
import data_prepration as data_prep
import histogram_plotter as plotter

TRAIN_FEATURE_FILE_NAME = '../data/results/features_just_data.csv'
TEST_FEATURE_FILE_NAME = '../data/results/test_just_data.csv'


class IsolationForestModel(object):
    def __init__(
            self,
            raw_train_file_name,
            col_names,
            contamination,
            scale_method,
            pickle=False
    ):
        self.raw_train_file_name = raw_train_file_name
        self.col_names = col_names
        self.contamination = contamination
        self.scale_method = scale_method
        self.minmax_scale = MinMaxScaler(feature_range=(0, 1))
        self.standard_scale = StandardScaler(with_mean=0, with_std=1)
        self.pickle = pickle

        # train the scalers
        raw_data = data_prep.get_data_frame_values(raw_train_file_name, col_names)
        self.minmax_scale.fit(raw_data)
        self.standard_scale.fit(raw_data)

        # Pickle scalers
        if pickle:
            ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
            joblib.dump(self.minmax_scale, '../data/results/' + str(contamination) + '_minmax_%s.pkl' % ts)
            joblib.dump(self.standard_scale, '../data/results/' + str(contamination) + '_standard_%s.pkl' % ts)

        # load and scale the training data
        if scale_method == data_prep.ScaleMethod.Normalize:
            self.scaled_train_data = self.minmax_scale.transform(raw_data)
        else:
            self.scaled_train_data == self.standard_scale.transform(raw_data)

        # fit the model
        # max_samples = "auto", then max_samples=min(256, n_samples).
        # contamination : float in (0., 0.5), optional (default=0.1)
        # random_state: the seed used by the random number generator
        rng = np.random.RandomState(42)
        self.clf = IsolationForest(contamination=contamination, n_jobs=-1, random_state=rng, verbose=1)
        self.clf.fit(self.scaled_train_data)

        # Pickle the model
        if pickle:
            ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
            joblib.dump(self.clf, '../data/results/' + str(contamination) + '_model_isof_%s.pkl' % ts)

    def get_scale_method(self):
        return self.scale_method

    def set_scale_method(self, scale_method):
        self.scale_method = scale_method

    def get_contamination(self):
        return self.contamination

    def set_contamination(self, cont):
        self.contamination = cont

    def get_minmax_scaler(self):
        return self.minmax_scale

    def get_standard_scaler(self):
        return self.standard_scale

    def get_scaled_dataset(self):
        return self.scaled_train_data

    def get_feature_names(self):
        return self.col_names

    def get_train_predictions(self):
        return self.clf.predict(self.scaled_train_data)

    def get_train_scores(self):
        return self.clf.decision_function(self.scaled_train_data)

    def get_scores(self, scaled_samples):
        return self.clf.decision_function(scaled_samples)

    def get_predictions(self, scaled_samples):
        # NOTE: samples should be scaled with the same scaling method that applied to the training dataset
        # Predict if a particular sample is an outlier or not.
        # Tells whether or not (+1 or -1) each sample should be considered as an inlier according to the fitted model.
        return self.clf.predict(scaled_samples)

    def is_outlier(self, new_data):
        # Reshape your data either using X.reshape(-1, 1) if your data has a single feature or
        # X.reshape(1, -1) if it contains a single sample.
        # The anomaly score of the input samples. The lower, the more abnormal
        scaled_data = None
        if self.scale_method == data_prep.ScaleMethod.Normalize:
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
        plt.title('PCA Plot of %d Samples\n Contamination = %s\nDimension reduction from %d to 2'
                  % (len(y_pred_samples), str(self.contamination), len(self.col_names)))
        plt.savefig('../data/diagrams/%s_%s.png' % (fig_name, ts), bbox_inches='tight')


def anomaly_score_finder(predictions, scores):
    score_list = []
    for x in np.ndenumerate(predictions):
        if x[1] == -1:
            score_list.append(scores[x[0][0]])
    return score_list


def run_experiments(model):
    cont = str(model.get_contamination())
    model.plot_data(TRAIN_FEATURE_FILE_NAME,
                    cont + '_train_data_plot')
    # train data plots
    # score histogram
    train_scores = model.get_train_scores()
    plotter.plot_histogram(train_scores, 'Histogram of train data scores, Contamination = ' + cont,
                           'Score',
                           'Samples', cont + '_train_scores', True, False)

    # outlier vs. inlier charts
    train_predictions = model.get_train_predictions()
    train_anomaly_scores = anomaly_score_finder(train_predictions, train_scores)
    plotter.plot_histogram(train_anomaly_scores, 'Histogram of train data anomaly scores, Contamination = ' + cont,
                           'Score',
                           'Samples', cont + '_train_anomaly_scores', True, False)
    outlier_count = len(train_anomaly_scores)
    inlier_count = len(train_predictions) - len(train_anomaly_scores)
    sizes = [outlier_count, inlier_count]
    plotter.plot_pie_chart(sizes,
                           'Distribution of Outliers (%s) vs. Inliers(%s), Contamination = %s' %(outlier_count,
                                                                                                 inlier_count,
                                                                                                 cont),
                           cont + '_train_pie')

    # test data
    raw_test_data = data_prep.get_data_frame_values(TEST_FEATURE_FILE_NAME, attribute_names.FEATURE_NAMES)
    scaled_test_data = model.get_minmax_scaler().transform(raw_test_data)

    # plots
    test_scores = model.get_scores(scaled_test_data)
    plotter.plot_histogram(train_scores, 'Histogram of test data scores, Contamination = ' + cont,
                           'Score',
                           'Samples', cont + '_test_scores', True, False)

    # outlier vs. inlier charts
    test_predictions = model.get_predictions(scaled_test_data)
    test_anomaly_scores = anomaly_score_finder(test_predictions, test_scores)
    plotter.plot_histogram(test_anomaly_scores, 'Histogram of test data anomaly scores, Contamination = ' + cont,
                           'Score',
                           'Samples', cont + '_test_anomaly_scores', True, False)
    outlier_count = len(test_anomaly_scores)
    inlier_count = len(test_predictions) - len(test_anomaly_scores)
    sizes = [outlier_count, inlier_count]
    plotter.plot_pie_chart(sizes,
                           'Distribution of Outliers (%s) vs. Inliers(%s), Contamination = %s' %(outlier_count,
                                                                                                 inlier_count,
                                                                                                 cont),
                           cont + '_test_pie')


# experiments and plots
from metadata import attribute_names
from data_prepration import ScaleMethod

# experiment 1
isolation_forest1 = IsolationForestModel(TRAIN_FEATURE_FILE_NAME,
                                         attribute_names.FEATURE_NAMES,
                                         0.0001,
                                         ScaleMethod.Normalize,
                                         pickle=True)
run_experiments(isolation_forest1)

# experiment 2
isolation_forest2 = IsolationForestModel(TRAIN_FEATURE_FILE_NAME,
                                         attribute_names.FEATURE_NAMES,
                                         0.001,
                                         ScaleMethod.Normalize,
                                         pickle=True)
run_experiments(isolation_forest2)

# experiment 3
isolation_forest3 = IsolationForestModel(TRAIN_FEATURE_FILE_NAME,
                                         attribute_names.FEATURE_NAMES,
                                         0.01,
                                         ScaleMethod.Normalize,
                                         pickle=True)
run_experiments(isolation_forest3)

# experiment 4
isolation_forest4 = IsolationForestModel(TRAIN_FEATURE_FILE_NAME,
                                         attribute_names.FEATURE_NAMES,
                                         0.1,
                                         ScaleMethod.Normalize,
                                         pickle=True)
run_experiments(isolation_forest4)


# new data
# new_data = [9,2.875,0.055,0.25,0.043,0.014,0.0,0.0,0.077,0.115,0.038,5.067,13.0,5.338,5.244,0.5]
# print isolation_forest1.is_outlier(new_data)
