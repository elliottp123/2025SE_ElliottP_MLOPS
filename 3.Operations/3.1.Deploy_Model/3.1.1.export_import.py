import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('style_Matplotlib_charts.mplstyle')
from sklearn.linear_model import LinearRegression
import pickle


def save_model ():
    training_data = pd.read_csv('course_specifications_data.csv', delimiter=',')
    x = np.array(training_data.iloc[:,1]).reshape(-1, 1)
    y = np.array(training_data.iloc[:,0])# Create the model
    my_model = LinearRegression()
    my_model.fit(x, y)
    filename = 'my_saved_model.sav'
    pickle.dump(my_model, open(filename, 'wb'))