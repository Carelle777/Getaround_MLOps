# 🚗 Getaround : prix de location et retards (MLOps)

Projet de certification Jedha Fullstack (RNCP38777) — **Carelle Nouko**

## 1. Le problème

Getaround est une application où des particuliers louent leur voiture. Deux questions se posent à l'entreprise :

1. **Les retards.** Quand un conducteur rend la voiture en retard, le conducteur suivant peut attendre, voire annuler. Faut-il imposer un **délai minimum** entre deux locations ? Et si oui, de combien de minutes ?
2. **Le prix.** Comment aider un propriétaire à **choisir le bon prix** par jour pour sa voiture ?

Mes deux livrables :
- un **dashboard** qui simule l'effet d'un délai minimum ;
- une **API** qui prédit un prix de location avec un modèle de Machine Learning.

## 2. Les liens en ligne

| Livrable | Lien |
|---|---|
| Dashboard (Streamlit) | https://getaroundmlopscarelle.streamlit.app |
| API (Render), documentation | https://getaround-api-carelle.onrender.com/docs |

⚠️ L'API et le dashboard sont hébergés sur des offres gratuites : s'ils n'ont pas servi depuis un moment, ils « dorment ». Le **premier chargement peut durer jusqu'à 1 minute**, c'est normal.

## 3. Les données

Deux fichiers fournis par Jedha, dans le dossier `data/` :

| Fichier | Contenu | Utilisé pour |
|---|---|---|
| `get_around_delay_analysis (1).xlsx` | Les locations, avec le retard au retour de la voiture et le délai avec la location précédente | Le dashboard |
| `get_around_pricing_project (1).csv` | Des voitures avec leurs caractéristiques (marque, kilométrage, carburant, options…) et leur prix par jour | Le modèle de prix |

Les noms contiennent un « (1) » : je les ai gardés tels quels, car le code les utilise.

## 4. Le dashboard (retards)

Il a deux parties :

1. **Distribution des retards** au retour de la voiture (un nombre négatif veut dire « en avance »). Le graphique est zoomé entre -200 et +200 minutes, car quelques retards extrêmes (jusqu'à plusieurs jours) le rendaient illisible. La phrase sous le graphique dit combien de locations sont laissées de côté (**2 522**).
2. **Simulateur de délai minimum.** On choisit un délai (de 0 à 120 minutes) et la voiture concernée (toutes, ou seulement celles avec Getaround **Connect**). Le dashboard compte les locations « impactées » : celles dont le **délai avec la location précédente est plus petit que le délai choisi**.

### Ce que j'ai trouvé

- Sur **1 841 locations** qui ont une location juste avant, **279** (15 %) ont un délai de **0 minute** : la voiture est reprise tout de suite.
- Les délais dans les données sont des multiples de 30 minutes (0, 30, 60, 90…).
- Avec un délai minimum de **30 minutes**, **279 locations (15,2 %)** seraient impactées. Avec **60 minutes**, **401 (21,8 %)**.
- Avec Connect seulement, à 30 minutes : **131 locations sur 813 (16,1 %)**.

### Un défaut que j'ai trouvé et corrigé

Mon premier calcul ignorait les délais de 0 minute (une condition `> 0`) et affichait donc **0 location impactée** à 30 minutes, ce qui était faux. En comptant à la main dans les données, j'ai trouvé 279 locations. J'ai corrigé le code et renommé les indicateurs : je mesure la **part des locations impactées**, pas une perte d'argent.

### Ce que montre le notebook d'analyse

Le notebook `notebooks/01-Getaround_analysis.ipynb` retrouve ces chiffres et va plus loin :

- **21 310 locations**, dont **3 265 annulées** (15,3 %).
- **57,5 %** des retours sont en retard, avec un retard médian de **9 minutes**. **26,8 %** dépassent une heure de retard.
- Dans **218 cas** sur 1 841, la voiture précédente est rendue après le début prévu de la suivante (112 locations ont un retard précédent inconnu et ne sont pas comptées).

| Délai minimum | Locations bloquées | Problèmes évités | Bloquées sans problème |
|---|---|---|---|
| 30 min | 279 (15,2 %) | 116 (53 %) | 163 |
| 60 min | 401 (21,8 %) | 146 (67 %) | 255 |
| 90 min | 584 (31,7 %) | 172 (79 %) | 412 |
| 120 min | 666 (36,2 %) | 180 (83 %) | 486 |

**Ma recommandation : un délai de 30 à 60 minutes.** Au-delà, on bloque beaucoup de locations qui n'avaient aucun problème pour très peu de problèmes évités en plus (de 60 à 90 minutes : +26 problèmes évités pour +183 locations bloquées).

En appliquant la règle **seulement aux voitures Connect**, on bloque moins (131 locations à 30 minutes) mais on évite aussi moins de problèmes (40, contre 116 pour toutes les voitures).

## 5. Le modèle de prix

**Fichier : `train.py`.**

1. Je lis les voitures et leur prix par jour (`rental_price_per_day`).
2. Je sépare **80 %** des voitures pour apprendre, **20 %** pour tester (`random_state=42`, pour toujours avoir le même résultat).
3. Je prépare les données dans un `Pipeline` : les nombres (kilométrage, puissance) sont mis à la même échelle (`StandardScaler`), les catégories (marque, carburant, couleur…) sont transformées en 0 et 1 (`OneHotEncoder`).
4. J'entraîne un **XGBoost** (100 arbres, `learning_rate=0.1`, `max_depth=5`).
5. Je mesure le score **R²** sur les 20 % de test et je l'enregistre dans **MLflow** (le « journal de bord » des entraînements).
6. Je sauvegarde le modèle dans `api/model.joblib`, que l'API utilise.

**Résultat : R² = 0,748.** Dit simplement, le modèle explique environ **75 %** des différences de prix entre les voitures.

## 6. L'API de prix

Elle est écrite avec **FastAPI**. Elle charge le modèle au démarrage et expose :

- `GET /` : vérifie que l'API est en ligne ;
- `POST /predict` : reçoit une voiture, renvoie un prix par jour.

Chaque voiture est une liste de 13 valeurs, **dans cet ordre** : `model_key`, `mileage`, `engine_power`, `fuel`, `paint_color`, `car_type`, `private_parking_available`, `has_gps`, `has_air_conditioning`, `automatic_car`, `has_getaround_connect`, `has_speed_regulator`, `winter_tires`.

Exemple (une Citroën de 140 411 km) :

```bash
curl -X POST "https://getaround-api-carelle.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -d '{"input": [["Citroën", 140411, 100, "diesel", "black", "convertible", true, true, false, false, true, true, true]]}'
```

Réponse : `{"prediction": [112.52...]}`, soit environ **112,5 par jour**.

On peut aussi tester dans le navigateur avec la page `/docs` (bouton « Try it out »).

## 7. Lancer le projet chez soi

```bash
git clone https://github.com/Carelle777/Getaround_MLOps.git
cd Getaround_MLOps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**L'API :**
```bash
uvicorn api.app:app --reload
# puis ouvrir http://localhost:8000/docs
```

**Le dashboard :**
```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

**Réentraîner le modèle** (MLflow n'est pas dans `requirements.txt`, car l'API n'en a pas besoin) :
```bash
pip install mlflow
python train.py
```

**Avec Docker** (c'est ce que fait Render) :
```bash
docker build -t getaround-api .
docker run -p 8000:8000 getaround-api
```

## 8. Structure du projet

```
Getaround_MLOps/
├── README.md
├── requirements.txt          (API)
├── Dockerfile                (API)
├── train.py                  (entraînement + MLflow)
├── mlflow.db                 (journal des entraînements)
├── api/
│   ├── app.py                (API FastAPI)
│   └── model.joblib          (modèle entraîné)
├── dashboard/
│   ├── app.py                (dashboard Streamlit)
│   └── requirements.txt      (dashboard)
├── notebooks/
│   └── 01-Getaround_analysis.ipynb   (analyse exploratoire)
└── data/                     (les deux fichiers de données)
```

## 9. Mes limites

- J'évalue le modèle avec **un seul score (R²)** et **un seul découpage** 80/20. Je n'ai pas fait de validation croisée ni cherché les meilleurs réglages.
- Le dashboard compte les locations dont le délai est trop court, mais il **ne mesure pas l'argent réellement perdu** ni combien de retards seraient évités.
- Les délais des données sont des multiples de 30 minutes : un seuil de 15 minutes donne le même résultat qu'un seuil de 30.
- L'API **ne vérifie pas** le contenu des 13 valeurs : une valeur absurde donnerait un prix absurde.
- Offres gratuites : le premier chargement de l'API et du dashboard peut être lent.

## 10. Petit lexique

- **API :** un guichet où un programme envoie une demande et reçoit une réponse.
- **MLOps :** les bonnes pratiques pour mettre un modèle en service (suivi, déploiement, test).
- **MLflow :** un journal de bord qui enregistre chaque entraînement et son score.
- **R² :** note de 0 à 1 (1 = parfait) qui dit à quel point le modèle suit les vrais prix.
- **XGBoost :** un modèle qui combine beaucoup de petits arbres de décision.
- **Pipeline :** une chaîne qui prépare les données puis prédit, toujours dans le même ordre.
- **Docker :** une boîte qui contient le programme et tout ce qu'il faut pour le faire tourner.
- **Délai minimum (threshold) :** le temps imposé entre la fin d'une location et le début de la suivante.

## 11. Outils

Python · pandas · scikit-learn · XGBoost · MLflow · FastAPI · Uvicorn · Pydantic · Streamlit · Plotly · Docker · Render · Streamlit Cloud