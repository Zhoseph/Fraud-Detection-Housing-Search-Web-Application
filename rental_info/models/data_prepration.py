import pandas
import numpy
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from datetime import datetime as dt
from aenum import Enum


class ScaleMethod(Enum):
    Normalize = 1
    Standardize = 2


def normalize_data(input_file_name, column_names, save_file=False):
    data_frame = pandas.read_csv(input_file_name, names=column_names)
    x_array = data_frame.values
    # Support Vector Machine algorithms are not scale invariant, so it is highly recommended to scale your data.
    # Scale value of each attribute to be in [0,1] range
    minmax_scale = MinMaxScaler(feature_range=(0, 1))
    normalized_x = minmax_scale.fit_transform(x_array)
    if save_file:
        # write to file
        ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
        output_file_name = '../data/results/normalized_features_%s_.csv' % ts
        numpy.savetxt(output_file_name, normalized_x, delimiter=",", fmt='%1.3f')
    return normalized_x


def standardize_data(input_file_name, column_names, save_file=False):
    data_frame = pandas.read_csv(input_file_name, names=column_names)
    x_array = data_frame.values
    # Support Vector Machine algorithms are not scale invariant, so it is highly recommended to scale your data.
    # The result of standardization (or Z-score normalization) is that the features will be rescaled to
    # a standard Gaussian distribution with a mean of 0 and a standard deviation of 1
    standardized_x = StandardScaler(with_mean=0, with_std=1).fit_transform(x_array)
    if save_file:
        # write to file
        ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
        output_file_name = '../data/results/standardized_features_%s_.csv' % ts
        numpy.savetxt(output_file_name, standardized_x, delimiter=",", fmt='%1.3f')
    return standardized_x


def get_scaled_data(input_file_name, column_names, scale_method):
    if scale_method == ScaleMethod.Normalize:
        return normalize_data(input_file_name, column_names)
    if scale_method == ScaleMethod.Standardize:
        return standardize_data(input_file_name, column_names)


def get_data_frame_values(feature_file_name, feature_names):
    data_frame = pandas.read_csv(feature_file_name, names=feature_names)
    x_data = data_frame.values
    return x_data

# from metadata import attribute_names
# normalize_data('../data/results/features_just_data.csv',
#                  attribute_names.FEATURE_NAMES, True)
