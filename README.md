# 🚗 Getaround - Optimisation des Prix et Retards (MLOps)

Ce projet implémente l'architecture MLOps pour l'entreprise Getaround. Il vise à résoudre deux problématiques métiers via la Data Science et le Machine Learning.

## 🎯 Objectifs
1. **Dashboard Produit :** Simuler l'impact financier de l'imposition d'un délai minimum entre deux locations pour pallier les retards.
2. **API de Pricing :** Suggérer un prix de location optimal aux propriétaires grâce à un algorithme de Machine Learning.

## 🏗 Architecture Technique (Bloc 5 RNCP)
* **Modélisation :** Pipeline Scikit-Learn et `XGBoost`.
* **Tracking MLOps :** Suivi des expérimentations et sérialisation via `MLflow`.
* **Backend API :** `FastAPI` + Serveur asynchrone `Uvicorn` (Validation des données via `Pydantic`).
* **Frontend Web :** `Streamlit` et `Plotly` pour la visualisation interactive.
* **Déploiement :** Conteneurisation `Docker` et hébergement Cloud.

## 🚀 Utilisation de l'API (Inférence)
L'API accepte les requêtes POST au format JSON sur la route `/predict` :
```bash
curl -X 'POST' \
  'URL_DE_TON_API/predict' \
  -H 'Content-Type: application/json' \
  -d '{
  "input": [
    ["Citroën", 140411, 100, "diesel", "black", "convertible", true, true, false, false, true, true, true]
  ]
}'