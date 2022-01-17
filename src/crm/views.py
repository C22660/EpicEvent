from django.http import Http404, HttpResponse
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters

from crm.models import Clients, Contracts, Events, EventStatus
from authentication.models import Users
from crm.serializers import ClientsDetailSerializer, ContractsSerializer, EventsSerializer
from crm.permissions import ClientsPermissions, ContractsPermissions, EventsPermissions
from crm.filters import ContractsFilterSet, EventsFilterSet

# ContractsSerializer, EventsSerializer
# from crm.permissions import

# Récupérer la liste de tous les clients (possibilité de filtrer contact commercial)
# Récupérer les détails d'un client via son id


class ClientsViewset(ModelViewSet):

    permission_classes = [IsAuthenticated, ClientsPermissions]
    serializer_class = ClientsDetailSerializer

    def get_queryset(self):
        # si l'url est /api/clients/, alors self.kwargs = {}
        # si l'url est /api/clients/2/, alors self.kwargs = {'pk': '2'}
        # Si je veux le détail d'un client, je retourne toutes les valeurs à la permission
        # (l'affichage du détail étant géré par modelVieSet)
        # Intégration de la recherche dans l'url :
        queryset = Clients.objects.all()
        client_name = self.request.query_params.get('client_name')
        client_email = self.request.query_params.get('client_email')
        compagny_name = self.request.query_params.get('compagny_name')
        if client_name is not None:
            queryset = queryset.filter(last_name=client_name)
        elif client_email is not None:
            queryset = queryset.filter(email=client_email)
        elif compagny_name is not None:
            queryset = queryset.filter(compagny_name=compagny_name)

        # et si pas de recherche dans l'URL, retour direct du queryset
        return queryset

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

    # Implémente le request User en sales_contact
    def perform_create(self, serializer):
        serializer.save(sales_contact=self.request.user)


# -------------------------------C O N T R A C T S -------------------------------------

    # GET: /clients/{id}/contracts/
    @action(detail=True, methods=['get', 'post'], permission_classes=[ContractsPermissions])
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

            self.check_object_permissions(request, Clients.objects.get(pk=pk))
            # client_name = self.request.query_params.get('client_name')
            # client_email = self.request.query_params.get('client_email')
            date_contract = self.request.query_params.get('date_contract')
            amount = self.request.query_params.get('amount')
            # if client_name is not None:
            #     queryset = queryset.filter(client__last_name=client_name)
            # elif client_email is not None:
            #     queryset = queryset.filter(client__email=client_email)
            if date_contract is not None:
                # Transformation de la date 2022-01-11 sous forme d'une liste ['2022', '01', '11']
                date_split = date_contract.split("-")
                queryset = queryset.filter(date_created__year=date_split[0],
                                           date_created__month=date_split[1],
                                           date_created__day=date_split[2])
            elif amount is not None:
                queryset = queryset.filter(amount=amount)

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
                # Ici, passage de obj à la permission via Clients.objects.get(pk=pk)
                self.check_object_permissions(request, Clients.objects.get(pk=pk))
                # Enregistrement du contrat par le serializer en lui adressant le client récupéré
                # dans le try précédent, grace au pk de l'url et l'auteur via request.user
                # contract = serializer.create(client=client, sales_contact=request.user)
                contract = serializer.create(client=client)
                return Response(contract, status=200)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # ------------------------------------------------------------------------------ #
        # Via @action, création de l'url : /clients/{id}/contracts/{id}/ ici, l'url n'est pas
        # le nom de la fonction mais remplacé par url_path. Comme pk, issue_id devient
        # récupérable
        # ------------------------------------------------------------------------------ #
    @action(detail=True, methods=['put', 'delete'], url_path='contracts/(?P<contract_id>\d+)',
            permission_classes=[ContractsPermissions])
    # @action(detail=True, methods=['put', 'delete'], url_path='contracts/(?P<contract_id>\d+)')
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
            self.check_object_permissions(request, Clients.objects.get(pk=pk))
            contract_modified = serializer.update(instance=contract_concerned.first(),
                                                  validated_data=request.data)

            # reserialization de contract_modified pour passage en Response
            contract_serialized = ContractsSerializer(instance=contract_modified).data

            return Response(contract_serialized, status=200)

        if request.method == "DELETE":
            # Vérification des permissions
            self.check_object_permissions(request, Clients.objects.get(pk=pk))
            # si permission, suppression du problème :
            contract_concerned.delete()

            return Response({"message": "Le contrat a bien été supprimé."}, status=200)

# --------------------------------------E V E N T S-------------------------------------

        # ------------------------------------------------------------------------------ #
        # Via @action, création de l'url : /clients/{id}/contracts/{id}/events/
        # ici, l'url n'est pas le nom de la fonction mais remplacé par url_path.
        # Comme pk, issue_id devient récupérable
        # ------------------------------------------------------------------------------ #
    @action(detail=True, methods=['post', 'get'],
            url_path='contracts/(?P<contract_id>\d+)/events', permission_classes=[EventsPermissions])
    # @action(detail=True, methods=['post', 'get'], url_path='contracts/(?P<contract_id>\d+)/events')
    def events(self, request, contract_id, pk=None):
        """Création d'un path /cleints/<id>/contracts/<id>/events pour créer, récupérer
         un évènnement"""
        # Vérification que le client existe
        try:
            client = Clients.objects.get(pk=pk)
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
                self.check_object_permissions(request, Clients.objects.get(pk=pk))
                # Enregistrement de l'évènement par le serializer en lui adressant le
                # contrat concerné dans le try précédent, grace au contract_id de l'url
                # !!! si, contract_concerned récupéré avec filter et non get,
                # il faut ajouter .first() car il s'agit alors d'un queryset et non plus
                # d'une instance avec get contract_concerned = Contracts.objects.get(pk=contract_id)
                event = serializer.create(client=client, contract_concerned=contract_concerned.first())
                return Response(event, status=200)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer les évènements d'un contrat
        if request.method == 'GET':
            # Vérification des permissions
            # self.check_object_permissions(request, Clients.objects.get(pk=pk))
            self.check_object_permissions(request, Events.objects.filter(contract=contract_id).filter(client=pk))
            # récupération des &vènements liés à un contrat
            event_for_contract = Events.objects.filter(contract=contract_id)
            serializer = EventsSerializer(event_for_contract, many=True)

            return Response(serializer.data, status=200)

        # ------------------------------------------------------------------------------ #
        # Via @action, création de l'url : /clients/{id}/contracts/{id}/events/{id}
        # ici, l'url n'est pas le nom de la fonction mais remplacé par url_path.
        # Comme pk, contract_id et event_id deviennent récupérables
        # ------------------------------------------------------------------------------ #
    @action(detail=True, methods=['get', 'put', 'delete'],
            url_path='contracts/(?P<contract_id>\d+)/events/(?P<event_id>\d+)',
            permission_classes=[EventsPermissions])
    # @action(detail=True, methods=['get', 'put', 'delete'],
    #         url_path='contracts/(?P<contract_id>\d+)/events/(?P<event_id>\d+)')
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
            self.check_object_permissions(request, Events.objects.get(pk=event_id))
            # Si la requête souhaite modifier le contact support, l'ID collecté dans la
            # request Data doit être convertie en users.object
            pk_contact = request.data.get("support_contact")
            pk_event_status = request.data.get("event_status")
            if pk_contact is not None and pk_event_status is None:
                contact = Users.objects.get(pk=pk_contact)
                serializer = EventsSerializer(data=request.data, partial=True)
                if serializer.is_valid():
                    # Re création d'un update dans le serializers.py car ajout de support_contact
                    # sous forme d'object et non de dict de request.data
                    event_modified = serializer.update(instance=event_concerned.first(),
                                                       validated_data=request.data,
                                                       support_contact=contact)
            elif pk_contact is None and pk_event_status is not None:
                ev_status = EventStatus.objects.get(pk=pk_event_status)
                serializer = EventsSerializer(data=request.data, partial=True)
                if serializer.is_valid():
                    # Re création d'un update dans le serializers.py car ajout de support_contact
                    # sous forme d'object et non de dict de request.data
                    event_modified = serializer.update(instance=event_concerned.first(),
                                                       validated_data=request.data,
                                                       event_status=ev_status)
            elif pk_contact is not None and pk_event_status is not None:
                contact = Users.objects.get(pk=pk_contact)
                ev_status = EventStatus.objects.get(pk=pk_event_status)
                serializer = EventsSerializer(data=request.data, partial=True)
                if serializer.is_valid():
                    # Re création d'un update dans le serializers.py car ajout de support_contact
                    # sous forme d'object et non de dict de request.data
                    event_modified = serializer.update(instance=event_concerned.first(),
                                                       validated_data=request.data,
                                                       support_contact=contact,
                                                       event_status=ev_status)
            else:
                serializer = EventsSerializer(data=request.data, partial=True)
                # Re création d'un update dans le serializers.py car ajout de support_contact
                # sous forme d'object et non de dict de request.data
                if serializer.is_valid():
                    event_modified = serializer.update(instance=event_concerned.first(),
                                                       validated_data=request.data)

            # reserialization de comment_modified pour passage en Response
            event_serialized = EventsSerializer(instance=event_modified).data
            return Response(event_serialized, status=200)

        if request.method == "DELETE":
            # Vérification des permissions
            # self.check_object_permissions(request, Clients.objects.get(pk=pk))
            self.check_object_permissions(request, Events.objects.get(pk=event_id))
            event_concerned.delete()

            return Response({"message": "L'évènement' a bien été supprimé."}, status=200)

        # Récupérer un évènement
        if request.method == "GET":
            # Vérification des permissions
            # self.check_object_permissions(request, Clients.objects.get(pk=pk))
            self.check_object_permissions(request, Events.objects.get(pk=event_id))
            # reserialization de comment_modified pour passage en Response
            event_find = EventsSerializer(instance=event_concerned.first()).data
            return Response(event_find, status=200)

#----------------------------------------------------------------------#
#                      Gestion de la recherche                        -#
#               au niveau de api/contracts et api/clients             -#
#       celle de api/clients gérée au sein du def get_queryset de     -#
#                   la class ClientsViewset(ModelViewSet)             -#
# ---------------------------------------------------------------------#


class ContractsListView(generics.ListAPIView):
    """
    Classe utlisée pour permettre les recherches au niveau
    de la route api/contracts
    """
    permission_classes = [IsAuthenticated]

    http_method_names = ['get']
    queryset = Contracts.objects.all()
    serializer_class = ContractsSerializer
    filter_backends = [filters.DjangoFilterBackend]
    # filterset_fields = ['client__last_name', 'client__compagny_name', 'client__email',
    #                     'date_created', 'amount']
    filterset_class = ContractsFilterSet


class EventsListView(generics.ListAPIView):
    """
    Classe utlisée pour permettre les recherches au niveau
    de la route api/events
    """
    permission_classes = [IsAuthenticated]

    http_method_names = ['get']
    queryset = Events.objects.all()
    serializer_class = EventsSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = EventsFilterSet
