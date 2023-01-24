import pandas as pd
import pickle
from .utils import main_route

model = None
dataset_path = "dataset_train.csv"
model_path = "models/model.pkl"

def load_model():
    print(main_route+model_path)
    return pickle.load(open(main_route+model_path, 'rb'))
    # model = load(model_path)

def load_dataset():
    df = pd.read_csv(dataset_path, delimiter=';')
    df = df.sort_values(by='Obfuscated name')
    # доделать