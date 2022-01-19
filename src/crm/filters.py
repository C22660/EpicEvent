from django_filters import rest_framework as filters

from crm.models import Contracts, Events


class ContractsFilterSet(filters.FilterSet):
    """Implements filters to be used with ContractsListView"""

    # icontains permet de ne pas être sensible à la casse
    # date_contract = DateFilter(field_name="date_created", lookup_expr='gte')
    email = filters.CharFilter(
        field_name="client__email", lookup_expr='icontains'
    )
    client_contact = filters.CharFilter(
        field_name="client__last_name", lookup_expr='icontains'
    )
    client_name = filters.CharFilter(
        field_name="client__compagny_name", lookup_expr='icontains'
    )
    # date_contract = filters.DateFilter(
    #     field_name='date_created', method='get_date_contract', label="date contract format")
    contract_date = filters.CharFilter(
        field_name='date_created', method='get_date_contract', label="date contract format")

    def get_date_contract(self, queryset, field_name, value):
        # Transformation de la date 2022-01-11 sous forme d'une liste ['2022', '01', '11']
        date_split = value.split("-")
        return queryset.filter(date_created__year=date_split[0],
                               date_created__month=date_split[1],
                               date_created__day=date_split[2])

    class Meta:
        model = Contracts
        fields = ['amount', 'contract_date', 'client__email', 'client__last_name',
                  'client__compagny_name']


class EventsFilterSet(filters.FilterSet):
    """Implements filters to be used with EventsListView"""

    # icontains permet de ne pas être sensible à la casse
    # event_date = DateFilter(field_name="event_date__date", lookup_expr='gte')
    email = filters.CharFilter(
        field_name="client__email", lookup_expr='icontains'
    )
    client_contact = filters.CharFilter(
        field_name="client__last_name", lookup_expr='icontains'
    )
    client_name = filters.CharFilter(
        field_name="client__compagny_name", lookup_expr='icontains'
    )

    event_date = filters.CharFilter(
        field_name='event_date', method='get_date_event', label="date contract format")

    def get_date_event(self, queryset, field_name, value):
        # Transformation de la date 2022-01-11 sous forme d'une liste ['2022', '01', '11']
        date_split = value.split("-")
        return queryset.filter(event_date__year=date_split[0],
                               event_date__month=date_split[1],
                               event_date__day=date_split[2])

    class Meta:
        model = Events
        fields = ['event_date', 'client__email', 'client__last_name', 'client__compagny_name']
