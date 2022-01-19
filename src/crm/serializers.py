from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from crm.models import Clients, Contracts, Events, EventStatus


class ClientsDetailSerializer(ModelSerializer):
    """Serialize la classe Clients"""

    class Meta:
        model = Clients
        fields = ['compagny_name', 'first_name', 'last_name', 'email', 'phone', 'mobile',
                  'date_created', 'date_updated', 'sales_contact']

    # Vérification que le nom de la compagnie n'existe pas déjà en cas de création
    # d'un nouveau client
    def validate_compagny_name(self, value):
        if Clients.objects.filter(compagny_name=value).exists():
            raise serializers.ValidationError('Client already exists')
        return value


class ContractsSerializer(ModelSerializer):
    """Serialize la classe Contracts"""

    class Meta:
        model = Contracts
        fields = ['id', 'sales_contact', 'client', 'date_created', 'date_updated', 'status', 'amount',
                  'payment_due']

    # def create(self, client=None, sales_contact=None):
    def create(self, client=None, sales_contact=None):
        print('self datas = ', self.validated_data)
        contract = Contracts(
            # sales_contact=sales_contact,
            sales_contact=sales_contact,
            client=client,
            amount=self.validated_data['amount'],
            payment_due=self.validated_data['payment_due'],
        )
        contract.save()

        # Resérialization de contract pour qu'il puisse être affiché, en Json, par le
        # httpResponse de la view
        contract_serialized = ContractsSerializer(instance=contract).data

        return contract_serialized


class EventsSerializer(ModelSerializer):
    """Serialize la classe Events"""

    class Meta:
        model = Events
        fields = ['id', 'client', 'date_created', 'date_updated', 'support_contact', 'event_status',
                  'attendees', 'event_date', 'note', 'contract']

    def create(self, client=None, contract_concerned=None):

        event = Events(
            contract=contract_concerned,
            client=client,
            event_status=self.validated_data['event_status'],
            event_date=self.validated_data['event_date'],
            note=self.validated_data['note'],
        )
        event.save()

        # Resérialization de comment pour qu'il puisse être affiché, en Json, par le
        # httpResponse de la view
        event_serialized = EventsSerializer(instance=event).data

        return event_serialized

    # Vu que l'ajout du contact support implique un user object et non juste son ID,
    # mise en place d'une def update en lieu et place de celle qui existe par défaut
    def update(self, instance, validated_data, support_contact=None, event_status=None):
        if support_contact is not None:
            instance.support_contact = support_contact
        if event_status is not None:
            instance.event_status = event_status
        if self.validated_data.get('event_date'):
            instance.event_date = self.validated_data['event_date']
        if self.validated_data.get('note'):
            instance.note = self.validated_data['note']
        instance.save()
        return instance
