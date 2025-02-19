import export_import
import pickle
import numpy as np


export_import.save_model()

loaded_model = pickle.load(open('my_saved_model.sav', 'rb'))
predict = np.array([4]).reshape(1, -1)
result = loaded_model.predict(predict)
print(result[0])
