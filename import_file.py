# Standard Scientific Import
from IPython.display import display, HTML, Javascript, set_matplotlib_formats
import numpy as np
import scipy as sp
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.pyplot import plot as plot
import sklearn
from joblib import Parallel, delayed
from numpy import inf, arange, array, linspace, exp, log, power, pi, cos, sin, radians, degrees
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
sns.set()
sns.set_style('whitegrid')
set_matplotlib_formats('png', 'pdf')
# set_matplotlib_formats('png','svg','pdf')


# Module Imports
from helpers.app_helper import *
from helpers.gmm_helper import *
from helpers.angular_linear import *
from helpers.plot_print_helper import *
from helpers.data_reader import *
from helpers.pre_process import *
from helpers.empirical_helper import *
from lib.lib_loader import *


# Custom Import
from scipy import integrate
from sklearn import mixture, neighbors
from math import ceil as ceil
from windrose import WindroseAxes, WindAxes
from scipy.stats import weibull_min, vonmises, beta
from sklearn.model_selection import GridSearchCV
import folium
from lmoments3 import distr