# Linear Solver

Un solveur de programmation linéaire basé sur l'algorithme du Simplex, développé comme une application Django REST.

## 📋 Description du Projet

Ce projet implémente un solveur pour les problèmes de programmation linéaire en utilisant l'algorithme du Simplex. Il fournit une API REST pour résoudre des problèmes d'optimisation linéaire et inclut une interface web pour faciliter l'utilisation.

## 📁 Structure du Projet

```
linear_solver/
├── linear_solver/          # Configuration principale Django
├── simplex/                # Application Django principale
│   ├── solvers/           # Implémentations des solveurs
│   ├── utils/             # Fonctions utilitaires
│   ├── static/            # Fichiers statiques (CSS, JS, images)
│   ├── templates/         # Templates HTML
│   ├── views.py           # Vues de l'API
│   ├── serializers.py     # Sérialiseurs DRF
│   ├── models.py          # Modèles de données
│   ├── urls.py            # Routes de l'application
│   ├── tests.py           # Tests unitaires
│   └── admin.py           # Configuration admin Django
├── requirements.txt       # Dépendances Python
├── manage.py             # Script de gestion Django
├── build.sh              # Script de build
├── db.sqlite3            # Base de données SQLite
└── rapport_technique.tex # Documentation technique
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Étapes d'installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/rogelio-cpu/linear_solver.git
   cd linear_solver
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Exécuter les migrations**
   ```bash
   python manage.py migrate
   ```

5. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

   Le serveur sera accessible à `http://localhost:8000/`

## 📦 Dépendances

- **Django** (>=4.2) - Framework web
- **Django REST Framework** - Pour créer l'API REST
- **Gunicorn** - Serveur WSGI
- **Whitenoise** - Serveur de fichiers statiques
- **NumPy** - Calculs numériques et matrices

Voir `requirements.txt` pour la liste complète des dépendances.

## 🛠️ Utilisation

### API Endpoints

L'application expose des endpoints REST pour soumettre et résoudre des problèmes de programmation linéaire.

Exemple d'utilisation :
```bash
curl -X POST http://localhost:8000/api/solve/ \
  -H "Content-Type: application/json" \
  -d '{
    "objective": [...],
    "constraints": [...]
  }'
```

### Interface Web

Une interface web est disponible pour interagir avec le solveur de manière conviviale.

## 🧪 Tests

Exécuter les tests unitaires :
```bash
python manage.py test
```

## 📊 Algorithme du Simplex

Ce projet implémente l'algorithme du Simplex pour résoudre les problèmes de programmation linéaire sous forme standard:

```
Maximiser (ou Minimiser): c^T * x
Sujet à: A * x <= b, x >= 0
```

Pour plus de détails sur l'implémentation et la théorie mathématique, consultez `rapport_technique.tex`.

## 🏗️ Build

Un script de build est fourni pour automatiser la compilation/préparation du projet :
```bash
./build.sh
```

## 📝 Documentation Technique

Une documentation technique détaillée est disponible dans `rapport_technique.tex`. Elle couvre:
- Les fondamentaux de la programmation linéaire
- L'algorithme du Simplex
- L'implémentation du projet
- Les cas d'usage et exemples

## 👨‍💻 Auteur

**Rogelio CPU**

## 📄 Licence

Ce projet est fourni tel quel. Consultez la licence du repository pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à:
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur le repository GitHub.

---

**Dernière mise à jour**: Février 2026
