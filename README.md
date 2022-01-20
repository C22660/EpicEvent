# Application CRM pour une entreprise d'évènementiel.

Elle permettra essentiellement aux utilisateurs de créer des clients, d'ajouter des contrats à ces clients et d'y attacher un évènement par contrat signé.
L'application exploite les points de terminaison d'API qui serviront les données.

Les endpoints sont répartis dans différents dossiers selon leurs usages :
- Gestion des logins ; gestion des clients ; gestion des contrats déclarés pour ces clients ; gestion des évènements associés aux contrats.
- En fonction de leur métier, les utilisateurs ont des permissions différentes.



Développement d'un API RESTful pour traiter les données relatives :
- au projets,
- à ses contributeurs, 
- aux problèmes relevés,
- aux commentaires associés.

## Structuration de l'API via Postman

L'API se structure autour de 2 collections :
1. Login
   
2. Global project
    * Clients (Clients)
    * Contrats (Contracts)
    * Evènements (Events)


Elles permettent d'acceder aux points de terminaison suivants :

|  #  | Point de   terminaison d'API                                                                   | Méthode HTTP | URI                                      |
|:---:|------------------------------------------------------------------------------------------------|:------------:|:-----------------------------------------|
|  1. | Inscription   de l'utilisateur                                                                 |     POST     | /signup/                                 |
|  2. | Connexion   de l'utilisateur                                                                   |     POST     | /login/                                  |
|  3. | Récupérer   la liste de tous les clients (clients) rattachés à l'utilisateur (user)   connecté |      GET     | /clients/                                |
|  4. | Créer   un client                                                                              |     POST     | /clients/                                |
|  5. | Récupérer   les détails d'un client (client) via son id                                        |      GET     | /clients/{id}/                           |
|  6. | Mettre   à jour un client                                                                      |      PUT     | /clients/{id}/                           |
|  7. | Supprimer   un client et ses contrats                                                          |    DELETE    | /clients/{id}/                           |
|  8. | Récupérer   la liste des contrats (contracts) liés à un client (client)                        |      GET     | /clients/{id}/contracts/                 |
|  9. | Créer   un contrat pour un client                                                              |     POST     | /clients/{id}/contracts/                 |
| 10. | Mettre   à jour un contrat pour un client                                                      |      PUT     | /clients/{id}/contracts/{id}             |
| 11. | Supprimer   un contrat d'un client                                                             |    DELETE    | /clients/{id}/contracts/{id}             |
| 12. | Créer   des évènements pour un contrat                                                         |     POST     | /clients/{id}/contracts/{id}/events/     |
| 13. | Récupérer   la liste de tous les évènements liés à un contrat                                  |      GET     | /clients/{id}/contracts/{id}/events/     |
| 14. | Modifier   un évènement                                                                        |      PUT     | /clients/{id}/contracts/{id}/events/{id} |
| 15. | Supprimer   un évènement                                                                       |    DELETE    | /clients/{id}/contracts/{id}/events/{id} |
| 16. | Récupérer   un évènement (event) via son id                                                    |      GET     | /clients/{id}/contracts/{id}/events/{id} |
| 17. | Faire   des recherches d'un contrat                                                            |      GET     | /contracts/                              |
| 18. | Faire   des recherches d'un évènement                                                          |      GET     | /events/                                 |

Retrouvez la [documentation Postman ici](https://documenter.getpostman.com/view/18184212/UVXojsiq).



## Informations d'installation et d'exécution avec venv et pip


**Configurations et exécution du programme**
Installation :
- Cloner ce dépôt de code à l'aide de la commande `$ git clone clone https://github.com/C22660/EpicEvent.git` (vous pouvez également télécharger le code [en temps qu'archive zip](https://github.com/C22660/EpicEvent/archive/refs/heads/master.zip))
- Rendez-vous depuis un terminal à la racine du répertoire EpicEvent avec la commande `$ cd EpicEvent`
- Créer un environnement virtuel pour le projet avec `$ python -m venv env` sous windows ou `$ python3 -m venv env` sous macos ou linux.
- Activez l'environnement virtuel avec `$ env\Scripts\activate` sous windows ou `$ source env/bin/activate` sous macos ou linux.
- Installez les dépendances du projet avec la commande `$ pip install -r requirements.txt`

Une fois cette installation effectuée :

- Appliquer les migrations dans la base de données : depuis le terminal > $ python manage.py migrate

- Création du superuser (utilisateur avec droits d'administration) :
depuis le terminal > `$ python manage.py createsuperuser`
entrer l'Email et le mot de passe (invisible lors de la frappe dans le terminal)

- Générez les données de status des évènements :
depuis le terminal > `$ python manage.py loaddata statusevents.json`

- Lancement du serveur :
depuis le terminal > `$ python manage.py runserver`

- Accès aux URLs depuis Postman :
Dans la barre d'adresse, ajouter http://127.0.0.1:8000/api suivi du endpoint souhaité.

## Technologies
Python 3.9
Package ajouté : django ; djangorestframework ; djangorestframework-simplejwt ; django-filter ;
                 psycopg2

## Auteur        
Cédric M
