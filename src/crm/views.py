from django.http import Http404, HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from crm.models import Clients, Contracts, Events
from crm.serializers import ClientsDetailSerializer, ContractsSerializer, EventsSerializer

# ContractsSerializer, EventsSerializer
# from crm.permissions import

# Récupérer la liste de tous les clients (possibilité de filtrer contact commercial)
# Récupérer les détails d'un client via son id


class ClientsViewset(ModelViewSet):

    # permission_classes = [IsAuthenticated, ProjectIsUserAuthorOrContributorPermissions]
    #
    serializer_class = ClientsDetailSerializer

    def get_queryset(self):
        # si l'url est /api/clients/, alors self.kwargs = {}
        # si l'url est /api/clients/2/, alors self.kwargs = {'pk': '2'}
        # Si je veux le détail d'un client, je retourne toutes les valeurs à la permission
        # (l'affichage du détail étant géré par modelVieSet)
        return Clients.objects.all()

    # Pour pouvoir faire un update partiel
    # https://tech.serhatteker.com/post/2020-09/enable-partial-update-drf/
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    # Surcharge du class DestroyModelMixin pour modifier le message retourné
    # à l'origine "return Response(status=status.HTTP_204_NO_CONTENT)"
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Le client et ses contrats associés ont bien été supprimés."},
                        status=200)

# -------------------------------C O N T R A C T S -------------------------------------

    # GET: /clients/{id}/contracts/
    # @action(detail=True, methods=['get', 'post'], permission_classes=[IssuesPermissions])
    @action(detail=True, methods=['get', 'post'])
    def contracts(self, request, pk=None):
        """Création d'un path /clients/<id>/contracts pour afficher les contrats d'un client,
        et en enregistrer de nouveaux """
        # récupération de <id> du projet dans /clients/<id>/issues via pk
        if request.method == "GET":
            # Vérification qu'il y a un contrat d'enregisté pour le client
            queryset = Contracts.objects.filter(client=pk)
            if not queryset:
                return HttpResponse({"Aucun contrat pour ce client, ou client inexistant."},
                                    status=404)

            # self.check_object_permissions(request, Clients.objects.get(pk=pk))
            serializer = ContractsSerializer(queryset, many=True)
            return Response(serializer.data, status=200)


        # Enregistrer un contrat pour un client
        if request.method == "POST":
            # Vérification que le client existe
            try:
                client = Clients.objects.get(pk=pk)
            except Clients.DoesNotExist:
                return HttpResponse({f"Le client {pk} n'existe pas."}, status=404)

            # Si vérification passée :
            # Informations partielles adressées au sérializer (pas le client puisque abs du body et
            # présent dans l'url)
            serializer = ContractsSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                # Si Informations partielles validées :
                # Vérification des permissions
                # PERMISSIONS !!!!!!!!!!
                # self.check_object_permissions(request, Clients.objects.get(pk=pk))
                # Enregistrement du contrat par le serializer en lui adressant le client récupéré
                # dans le try précédent, grace au pk de l'url et l'auteur via request.user
                contract = serializer.create(client=client, sales_contact=request.user)
                return Response(contract, status=200)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # ------------------------------------------------------------------------------ #
        # Via @action, création de l'url : /clients/{id}/contracts/{id}/ ici, l'url n'est pas
        # le nom de la fonction mais remplacé par url_path. Comme pk, issue_id devient
        # récupérable
        # ------------------------------------------------------------------------------ #
    # @action(detail=True, methods=['put', 'delete'], url_path='clients/(?P<contract_id>\d+)',
    #         permission_classes=[ContractPermissions])
    @action(detail=True, methods=['put', 'delete'], url_path='clients/(?P<contract_id>\d+)')
    def update_or_delete_contract(self, request, contract_id, pk=None):
        """Création d'un path /clients/<id>/contracts/<id> pour mettre à jour un contrat,
        ou le supprimer"""
        # Vérification que le projet existe
        try:
            Clients.objects.get(pk=pk)
        except Clients.DoesNotExist:
            return HttpResponse({f"Le client {pk} n'existe pas."}, status=404)

        # récupération des contrats liés au client
        contract_concerned = Contracts.objects.filter(client=pk).filter(pk=contract_id)
        # Si aucun problème n'est associé à ce projet, alors len = 0 :
        if len(contract_concerned) == 0:
            return HttpResponse({f"Aucun contrat {contract_id} associé au client {pk}."},
                                status=404
                                )

        if request.method == "PUT":
            serializer = ContractsSerializer(partial=True)
            # Pas de création d'un update dans le serializers.py car utilisation de update()
            # Vérification des permissions
            # self.check_object_permissions(request, Projects.objects.get(pk=pk))
            contract_modified = serializer.update(instance=contract_concerned.first(),
                                                  validated_data=request.data)

            # reserialization de contract_modified pour passage en Response
            contract_serialized = ContractsSerializer(instance=contract_modified).data

            return Response(contract_serialized, status=200)

        if request.method == "DELETE":
            # Vérification des permissions
            # self.check_object_permissions(request, Projects.objects.get(pk=pk))
            # si permission, suppression du problème :
            contract_concerned.delete()

            return Response({"message": "Le contrat a bien été supprimé."}, status=200)

# --------------------------------------E V E N T S-------------------------------------

        # ------------------------------------------------------------------------------ #
        # Via @action, création de l'url : /clients/{id}/contracts/{id}/events/
        # ici, l'url n'est pas le nom de la fonction mais remplacé par url_path.
        # Comme pk, issue_id devient récupérable
        # ------------------------------------------------------------------------------ #
    # @action(detail=True, methods=['post', 'get'],
    #         url_path='contracts/(?P<contract_id>\d+)/events', permission_classes=[EventsPermissions])
    @action(detail=True, methods=['post', 'get'], url_path='contracts/(?P<contract_id>\d+)/events')
    def events(self, request, contract_id, pk=None):
        """Création d'un path /cleints/<id>/contracts/<id>/events pour créer, récupérer
         un évènnement"""
        # Vérification que le client existe
        try:
            Clients.objects.get(pk=pk)
        except Clients.DoesNotExist:
            return HttpResponse({f"Le client {pk} n'existe pas."}, status=404)

        # Vérification qu'il y a bien un contrat 'contract_id' lié au client
        contract_concerned = Contracts.objects.filter(client=pk).filter(pk=contract_id)
        # Si aucun problème n'est associé à ce projet, alors len = 0 :
        if len(contract_concerned) == 0:
            return HttpResponse({f"Aucun contrat {contract_id} associé au client {pk}."},
                                status=404
                                )
        # Enregistrer un évènement pour un contrat
        if request.method == "POST":
            # Informations partielles adressées au sérializer (pas l'ID de l'issue puisque abs
            # du body et présent dans l'url).

            serializer = EventsSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                # Si Informations partielles validées :
                # Vérification des permissions
                # self.check_object_permissions(request, Projects.objects.get(pk=pk))
                # Enregistrement de l'évènement par le serializer en lui adressant le
                # contrat concerné dans le try précédent, grace au contract_id de l'url
                # !!! si, contract_concerned récupéré avec filter et non get,
                # il faut ajouter .first() car il s'agit alors d'un queryset et non plus
                # d'une instance avec get contract_concerned = Contracts.objects.get(pk=contract_id)
                event = serializer.create(contract_concerned=contract_concerned.first())
                return Response(event, status=200)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer les évènements d'un contrat
        if request.method == 'GET':
            # Vérification des permissions
            # self.check_object_permissions(request, Clients.objects.get(pk=pk))
            # récupération des &vènements liés à un contrat
            event_for_contract = Events.objects.filter(contract=contract_id)
            # datas = []
            # for comment in all_comments_for_issue:
            #     serializer = CommentsSerializer(comment)
            #     datas.append(serializer.data)

            return Response(event_for_contract, status=200)

        # ------------------------------------------------------------------------------ #
        # Via @action, création de l'url : /clients/{id}/contracts/{id}/events/{id}
        # ici, l'url n'est pas le nom de la fonction mais remplacé par url_path.
        # Comme pk, contract_id et event_id deviennent récupérables
        # ------------------------------------------------------------------------------ #
    # @action(detail=True, methods=['get', 'put', 'delete'],
    #         url_path='contracts/(?P<contract_id>\d+)/events/(?P<event_id>\d+)',
    #         permission_classes=[EventsPermissions])
    @action(detail=True, methods=['get', 'put', 'delete'],
            url_path='contracts/(?P<contract_id>\d+)/events/(?P<event_id>\d+)')
    def update_or_delete_or_get_event(self, request, contract_id, event_id, pk=None):
        """Création d'un path /clients/<id>/contract/<id>/event/<id> pour créer, récupérer,
        modifier, supprimer un évènement"""
        # Vérification qu'il y a bien un client pk
        try:
            Clients.objects.get(pk=pk)
        except Clients.DoesNotExist:
            return HttpResponse({f"Le client {pk} n'existe pas."}, status=404)

        # Vérification qu'il y a bien un contrat 'contrat_id' lié au client
        contract_concerned = Contracts.objects.filter(client=pk).filter(pk=contract_id)
        # Si aucun contrat n'est associé à ce client, alors len = 0 :
        if len(contract_concerned) == 0:
            return HttpResponse({f"Aucun contrat {contract_id} associé au client {pk}."},
                                status=404
                                )
        # Enfin, vérification que l'évènement existe et est bien lié à contract_id
        event_concerned = Events.objects.filter(pk=event_id).filter(contract=contract_id)

        # Si aucun évènement n'est associé à ce contract, alors len = 0 :
        if len(event_concerned) == 0:
            return HttpResponse({f"Aucun évènement {event_id} associé au contrat {contract_id}."},
                                status=404
                                )

        # Modifier un évènement
        if request.method == "PUT":
            # Vérification des permissions
            # self.check_object_permissions(request, Clients.objects.get(pk=pk))
            serializer = EventsSerializer(partial=True)

            # Pas de création d'un update dans le serializers.py car utilisation de update()
            event_modified = serializer.update(instance=event_concerned.first(),
                                                 validated_data=request.data)

            # reserialization de comment_modified pour passage en Response
            event_serialized = EventsSerializer(instance=event_modified).data

            return Response(event_serialized, status=200)

        if request.method == "DELETE":
            # Vérification des permissions
            # self.check_object_permissions(request, Clients.objects.get(pk=pk))
            event_concerned.delete()

            return Response({"message": "L'évènement' a bien été supprimé."}, status=200)

        # Récupérer un évènement
        if request.method == "GET":
            # Vérification des permissions
            # self.check_object_permissions(request, Clients.objects.get(pk=pk))
            # reserialization de comment_modified pour passage en Response
            event_find = EventsSerializer(instance=event_concerned.first()).data
            return Response(event_find, status=200)

