---

# WebWatcher

## 🎯 Objectif du projet

WebWatcher est un **script de surveillance automatique de pages web**.
Son rôle est de vérifier régulièrement une page et de déclencher une **alerte** si son contenu a été modifié.

Le projet a été réalisé dans le cadre d’un rattrapage académique afin de montrer la mise en place d’un outil simple mais robuste, mêlant **programmation Python**, **méthodes de détection de changements** et **bonnes pratiques de cybersécurité**.

---

## 📚 Contexte et état de l’art

La surveillance de pages web répond à de nombreux besoins :

* Suivre l’évolution des prix sur un site e-commerce.
* Être averti lorsqu’un document est publié sur un site institutionnel.
* Détecter une altération suspecte de contenu pouvant signaler une attaque informatique.

Il existe déjà des solutions en ligne comme **Distill.io**, **VisualPing** ou **Changedetection.io**.
Cependant, ces services sont souvent limités (version gratuite bridée, dépendance à des serveurs tiers, faible personnalisation).

L’objectif de ce projet est donc de développer une **solution personnelle** et **maîtrisée**, capable d’être adaptée à différents besoins et documentée de bout en bout.

---

## 🛠️ Choix techniques et méthodologie

* **Langage :** Python 3 (simplicité, portabilité, riche écosystème).
* **Bibliothèques principales :**

  * `requests` : récupération des pages web via HTTP.
  * `hashlib` : calcul d’une empreinte (SHA-256) du contenu.
  * `beautifulsoup4` : filtrage optionnel de zones HTML (ignorer publicités, timestamps, etc.).
  * `sqlite3` : stockage d’un historique complet des vérifications.
* **Méthode de détection :**

  * Normalisation du HTML (retours à la ligne, espaces).
  * Calcul d’un hash.
  * Comparaison avec la valeur précédente enregistrée.
* **Alerte :**

  * Affichage en console + log.
  * Historique stocké en SQLite pour analyse.
* **Robustesse :**

  * Gestion des timeouts et codes HTTP.
  * Pas d’écrasement d’état en cas d’erreur.
  * Écriture atomique du fichier d’état.

---

## 📂 Structure du projet

```
Webwatcher/
├── webwatcher.py          # Script principal (CLI)
├── app.py                 # Serveur Flask de test (page modifiable)
├── core/                  # Modules principaux
│   ├── fetcher.py         # Récupération de page web
│   ├── sanitizer.py       # Nettoyage / filtrage du HTML
│   ├── hasher.py          # Normalisation + hash SHA-256
│   ├── storage.py         # Gestion état + historique
│   └── notifier.py        # Alerte (console/log)
├── data/                  # Contient les fichiers générés (non versionnés)
│   └── .gitkeep
├── requirements.txt       # Dépendances
└── README.md              # Ce document
```

---

## 🚀 Installation

1. Cloner le dépôt :

```bash
git clone https://github.com/Daniel-0ps/Webwatcher.git
cd Webwatcher
```

2. Créer un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## 🖥️ Utilisation

### Vérification simple d’une page

```bash
python webwatcher.py --url http://127.0.0.1:5000/
```

➡️ Premier lancement : enregistre un état de référence.
➡️ Lancements suivants : compare et alerte si changement.

### Mode surveillance continue (toutes les 60s)

```bash
python webwatcher.py --url https://example.com --interval 60
```

### Ignorer des éléments dynamiques (pubs, timestamps)

```bash
python webwatcher.py --url http://127.0.0.1:5000/ \
  --ignore ".banner,#ts" --log-level INFO
```

### Autres options utiles

* `--state ./data/state.json` : fichier d’état minimal.
* `--history ./data/history.sqlite` : base SQLite d’historique.
* `--timeout 10` : délai max pour récupérer la page.
* `--log-file ./data/webwatcher.log` : enregistre les logs.
* `--log-level DEBUG|INFO|WARNING|ERROR`.

---

## 🔎 Comment tester le projet

### 1. Test basique sur une page existante

1. Lancer une première vérification sur `http://127.0.0.1:5000/`.
2. Relancer la même commande → devrait afficher “Aucun changement détecté”.

### 2. Test avec modification (serveur local inclus)

1. Lancer le serveur de test :

   ```bash
   python app.py
   ```

   Cela démarre une page web locale accessible sur `http://127.0.0.1:5000/`.

2. Surveiller la page avec WebWatcher :

   ```bash
   python webwatcher.py --url http://127.0.0.1:5000/
   ```

3. Modifier le fichier `data/content.txt` (ajouter ou supprimer une ligne).

4. Relancer WebWatcher → une alerte “\*\*\* ALERTE \*\*\* Changement détecté.” s’affiche.

### 3. Test des options avancées

* Avec `--ignore ".banner,#ts"`, on peut ignorer la bannière et le timestamp générés dynamiquement par Flask.
* En mode `--interval 30`, WebWatcher vérifie automatiquement toutes les 30 secondes.
* Les logs sont sauvegardés dans `data/webwatcher.log` et l’historique complet dans `data/history.sqlite`.

---

## 📑 Résultats attendus (exemple de logs)

```
2025-08-26 22:31:54 INFO    Fetch http://127.0.0.1:5000/ (200, 1256 bytes)
2025-08-26 22:31:54 INFO    No change detected.
2025-08-26 22:34:02 WARNING *** ALERTE *** Changement détecté.
2025-08-26 22:34:02 INFO    State updated • state=./data/state.json
```

---

## 🔐 Bonnes pratiques & limites

* **Ne pas lancer WebWatcher sur des sites sensibles** ou en boucle trop rapide → risque de surcharge.
* Respecter le fichier `robots.txt` quand c’est pertinent.
* Le script détecte un **changement global** de page : il ne précise pas exactement *où* la modification a eu lieu.
* Les pages générées par JavaScript ne sont pas gérées (évolution possible avec Selenium).

---
