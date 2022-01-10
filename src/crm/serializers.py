from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from crm.models import Clients, Contracts, Events


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
        fields = ['sales_contact', 'client', 'date_created', 'date_update', 'status', 'amount',
                  'payment_due']

    def create(self, client=None, sales_contact=None):

        contract = Contracts(
            sales_contact=sales_contact,
            client=client,
            date_created=self.validated_data['date_created'],
            date_update=self.validated_data['date_update'],
            status=self.validated_data['status'],
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
        fields = ['client', 'date_created', 'date_updated', 'support_contact', 'event_status',
                  'attendees', 'event_date', 'note', 'contract']

    def create(self, contract_concerned=None):

        event = Events(
            contract=contract_concerned,
            client=self.validated_data['client'],
            date_created=self.validated_data['date_created'],
            date_updated=self.validated_data['date_updated'],
            support_contact=self.validated_data['support_contact'],
            event_status=self.validated_data['event_status'],
            attendees=self.validated_data['attendees'],
            event_date=self.validated_data['event_date'],
            note=self.validated_data['note'],
        )
        event.save()

        # Resérialization de comment pour qu'il puisse être affiché, en Json, par le
        # httpResponse de la view
        event_serialized = EventsSerializer(instance=event).data

        return event_serialized
