from django.urls import path

from crm.views import ContractsListView, EventsListView

app_name = 'crm'

urlpatterns = [
    path('contracts', ContractsListView.as_view(), name="contracts_list"),
    path('events', EventsListView.as_view(), name="events_list"),
]
