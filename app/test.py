import pandas as pd
import pickle
from utils import *

model = None
dataset_path = "dataset_train.csv"
model_path = "model.pkl"

def load_model():
    return pickle.load(open(main_route+model_path, 'rb'))

model = load_model()
print(model)