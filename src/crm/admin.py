from django.contrib import admin

# Register your models here.
from crm.models import Clients, Events, Contracts, EventStatus


@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    pass


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    pass


@admin.register(Contracts)
class ContractsAdmin(admin.ModelAdmin):
    pass


@admin.register(EventStatus)
class EventStatusAdmin(admin.ModelAdmin):
    pass
