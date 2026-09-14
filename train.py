import pandas as pd
import mlflow
import mlflow.sklearn
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from xgboost import XGBRegressor
from sklearn.metrics import r2_score

# 1. Chargement des données
print("⏳ Chargement des données de tarification...")
df = pd.read_csv("data/get_around_pricing_project (1).csv")
df = df.drop("Unnamed: 0", axis=1, errors="ignore")

# 2. Séparation des features (X) et de la cible (y)
X = df.drop("rental_price_per_day", axis=1)
y = df["rental_price_per_day"]

# Séparation en jeu d'Entraînement et de Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Pipeline de Preprocessing (L'usine de nettoyage automatique)
numeric_features = ["mileage", "engine_power"]
categorical_features = [col for col in X.columns if col not in numeric_features]

numeric_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(drop="first", handle_unknown="ignore")

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ]
)

# 4. Définition du Modèle (Le Cerveau)
model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)

# Création du pipeline complet : Nettoyage + Prédiction
pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", model)
])

# 5. Tracking de l'expérience avec MLflow (Le Journal de bord)
print("🚀 Début de l'entraînement sous la surveillance de MLflow...")
mlflow.set_experiment("Getaround_Pricing_Optimization")

with mlflow.start_run():
    # L'entraînement réel de la machine
    pipeline.fit(X_train, y_train)
    
    # Prédictions sur le jeu de test pour évaluer l'IA
    predictions = pipeline.predict(X_test)
    score = r2_score(y_test, predictions)
    print(f"✅ Entraînement terminé. Précision du modèle (R2 Score) : {score:.3f}")
    
    # Enregistrement des données dans MLflow
    mlflow.log_param("model_type", "XGBoost")
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("r2_score", score)
    
    # Sauvegarde du modèle dans les dossiers internes de MLflow avec autorisation de sécurité
    mlflow.sklearn.log_model(
        pipeline, 
        "model", 
        skops_trusted_types=["xgboost.core.Booster", "xgboost.sklearn.XGBRegressor"]
    )

# 6. Industrialisation : Sauvegarde physique du modèle pour l'API
joblib.dump(pipeline, "api/model.joblib")
print("💾 Le cerveau artificiel a été exporté avec succès dans 'api/model.joblib' !")