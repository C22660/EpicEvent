from django_filters import rest_framework as filters, DateFilter

from crm.models import Contracts, Events


class ContractsFilterSet(filters.FilterSet):
    """Implements filters to be used with ContractsListView"""

    # icontains permet de ne pas être sensible à la casse
    date = DateFilter(field_name="date_created", lookup_expr='gte')
    email = filters.CharFilter(
        field_name="client__email", lookup_expr='icontains'
    )
    client_contact = filters.CharFilter(
        field_name="client__last_name", lookup_expr='icontains'
    )
    client_name = filters.CharFilter(
        field_name="client__compagny_name", lookup_expr='icontains'
    )

    class Meta:
        model = Contracts
        fields = ['amount', 'date', 'client__email', 'client__last_name', 'client__compagny_name']


class EventsFilterSet(filters.FilterSet):
    """Implements filters to be used with EventsListView"""

    # icontains permet de ne pas être sensible à la casse
    event_date = DateFilter(field_name="event_date", lookup_expr='gte')
    email = filters.CharFilter(
        field_name="client__email", lookup_expr='icontains'
    )
    client_contact = filters.CharFilter(
        field_name="client__last_name", lookup_expr='icontains'
    )
    client_name = filters.CharFilter(
        field_name="client__compagny_name", lookup_expr='icontains'
    )

    class Meta:
        model = Events
        fields = ['event_date', 'client__email', 'client__last_name', 'client__compagny_name']
