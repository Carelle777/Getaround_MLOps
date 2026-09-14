from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Any
import pandas as pd
import joblib

# 1. Initialisation de l'API (Le Guichet)
app = FastAPI(
    title="🚗 Getaround Pricing API",
    description="API de recommandation de prix de location utilisant le Machine Learning.",
    version="1.0"
)

# 2. Chargement du modèle entraîné (Le Cerveau)
# Dès que le serveur s'allume, il charge le fichier .joblib en mémoire
model = joblib.load("api/model.joblib")

# 3. Définition du contrat de données (Pydantic)
# Le cahier des charges exige exactement ce format : {"input": [[valeur1, valeur2, ...]]}
class PredictData(BaseModel):
    input: List[List[Any]]

# 4. Route par défaut (Pour vérifier que le serveur ne dort pas)
@app.get("/")
def read_root():
    return {"message": "L'API Getaround est en ligne. Ajoutez /docs à la fin de l'URL pour voir la documentation."}

# 5. Route de Prédiction (L'Endpoint /predict demandé par le client)
@app.post("/predict")
def predict_price(data: PredictData):
    # Liste exacte des colonnes dans le même ordre que lors de l'entraînement
    columns = [
        "model_key", "mileage", "engine_power", "fuel", "paint_color",
        "car_type", "private_parking_available", "has_gps", 
        "has_air_conditioning", "automatic_car", "has_getaround_connect",
        "has_speed_regulator", "winter_tires"
    ]
    
    # Transformation de la liste reçue (JSON) en tableau Pandas compréhensible par le modèle
    df = pd.DataFrame(data.input, columns=columns)
    
    # Le modèle XGBoost fait sa prédiction
    predictions = model.predict(df)
    
    # On renvoie la réponse au format JSON exigé
    return {"prediction": predictions.tolist()}