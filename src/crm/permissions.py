from django.db.models.query import QuerySet

from crm.models import Clients, Contracts, Events

from rest_framework.permissions import BasePermission


# ------- L'admin à accès à toutes les autorisations, un gestionnaire
# doit pouvoir afficher et modifier toutes les données du CRM--------

class IsUserIsManagementTeam(BasePermission):
    """Permission utilisée pour la création des utilisateurs, réservée aux gestionnaires.
    Vérification que l'utilisateur est membre de l'équipe gestion"""

    message = "Permission refusée : seul un gestionnaire peut créer un utilisateur"

    def has_permission(self, request, view):
        # Ne donnons l’accès qu’aux utilisateurs gestionnaires ou admin
        return bool(request.user and (request.user.is_management or request.user.is_admin))


class ClientsPermissions(BasePermission):
    """Vérifie les permissions au niveau du client. Seul un commercial à accès à
    l'ensemble du CRUD. Un gestionnaire n'aura accès qu'à la lecture et l'update.
     Le support n'aura accès qu'à la lecture"""

    # Attention : ici la permission ne fonctionne pas sans appel spécifique dans la vue,
    # car pas gérée automatiquement par le ModelVieSet et les classes permissions.
    # Seules les vues génériques (comme pour les projets) gèrent automatiquement
    # ".check_object_permissions(request, obj)"
    # view.kwargs["pk"] idem obj.pk, soit l'ID du projet

    message = "Permission refusée : seul un commercial peut créer un client (puis le modifier)." \
              "Un gestionnaire peut le modifier et un support peut le consulter."

    def has_permission(self, request, view):
        print("authentifié dans Clients Permissions")
        client_file = Clients.objects.get(pk=view.kwargs["pk"])
        commercial_attached_to_client = client_file.sales_contact
        sales_methods = ("GET", "PUT", "DELETE",)
        management_methods = ("GET", "PUT",)
        support_methods = ("GET",)
        print("request user = ", request.user)
        # le super user (ici remplacé par admin) à tous pouvoirs
        if request.user.is_authenticated:
            # return True

            # Ici, def has_object_permission(self, request, view, obj) supprimé,
            # car nous sommes au niveau de la class et non considéré comme
            # object. D'où lrintégration des vérifications dans has_permissions
            if request.user.is_admin:
                return True

            if request.user.is_sales and request.method in request.method == "POST":
                return True

            if (request.user.is_sales and request.user == commercial_attached_to_client
                    and request.method in sales_methods):
                return True

            if request.user.is_management and request.method in management_methods:
                print("request.user.is_management")
                return True

            if request.user.is_support and request.method in support_methods:
                print("request.user.is_support")
                return True

        return False


class ContractsPermissions(BasePermission):
    """Vérifie les permissions au niveau du contrat. Seul un commercial à accès à
    l'ensemble du CRUD. Un gestionnaire n'aura accès qu'à la lecture et l'update.
     Le support n'aura aucun accès"""

    # Attention : ici la permission ne fonctionne pas sans appel spécifique dans la vue,
    # car pas gérée automatiquement par le ModelVieSet et les classes permissions.
    # Seules les vues génériques (comme pour les projets) gèrent automatiquement
    # ".check_object_permissions(request, obj)"
    # view.kwargs["pk"] idem obj.pk, soit l'ID du client

    message = "Permission refusée : seul le commercial attaché au client peut créer un contrat." \
              "Un gestionnaire peut le modifier."

    def has_permission(self, request, view):
        print("authentifié dans Contracts Permissions")
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        # AU NIVEAU DES OBJETS 'CLIENTS' (MODEL CLIENTS)
        client_file = Clients.objects.get(pk=view.kwargs["pk"])
        commercial_attached_to_client = client_file.sales_contact
        sales_methods = ("GET", "POST", "PUT", "DELETE",)
        management_methods = ("GET", "PUT",)

        # le super user (ici remplacé par admin) à tous pouvoirs
        if request.user.is_admin:
            return True

        if (request.user.is_sales and request.user == commercial_attached_to_client
                and request.method in sales_methods):
            return True

        if request.user.is_management and request.method in management_methods:
            return True

        return False


class EventsPermissions(BasePermission):
    """Vérifie les permissions au niveau de l'évènement. Seul un commercial à accès à
    l'ensemble du CRUD. Un gestionnaire et un support pourront le modifier."""

    # Attention : ici la permission ne fonctionne pas sans appel spécifique dans la vue,
    # car pas gérée automatiquement par le ModelVieSet et les classes permissions.
    # Seules les vues génériques (comme pour les projets) gèrent automatiquement
    # ".check_object_permissions(request, obj)"
    # view.kwargs["pk"] idem obj.pk, soit l'ID du client

    message = "Permission refusée : seul le commercial attaché au client peut créer un évènement." \
              "Un gestionnaire peut ajouter un contact support"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            print("authentifié dans Events Permissions")
            return True

    def has_object_permission(self, request, view, obj):
        # AU NIVEAU DES OBJETS 'CLIENTS' (MODEL CLIENTS)
        # lors du GET, l'obj adressé à la permission et celui des évènements
        # liés au contrat. Comme adressé avec filter, c'est un queryset.
        # Il faut donc ittérer dedans pour accéder aux objets qu'il contient.
        # Dans le cas présent, vu qu'il y a un évènement par contrat (et vice versa)
        # on peut accéder au seul évènement adressé, et donc à son support contact
        if obj and not isinstance(obj, Clients):
            if isinstance(obj, QuerySet):
                support_attached_to_event = obj[0].support_contact
            else:
                support_attached_to_event = obj.support_contact
        # le queryset est adressé avec l'url clients/{id}/contracts/{id}/Events
        # l'objet avec l'url clients/{id}/contracts/{id}/Events/{id}

        client_file = Clients.objects.get(pk=view.kwargs["pk"])
        commercial_attached_to_client = client_file.sales_contact

        sales_methods = ("GET", "POST", "PUT", "DELETE",)
        management_methods = ("GET", "PUT",)
        support_methods = ("GET", "PUT",)

        # le super user (ici remplacé par admin) à tous pouvoirs
        if request.user.is_admin:
            return True

        if (request.user.is_sales and request.user == commercial_attached_to_client
                and request.method in sales_methods):
            return True

        if request.user.is_management and request.method in management_methods:
            return True

        if (request.user.is_support and request.user == support_attached_to_event
                and request.method in support_methods):
            return True

        return False
