from django.contrib import admin

# Register your models here.
from crm.models import Clients, Events, Contracts, EventStatus


@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_admin:
            return qs
        if request.user.is_management:
            return qs
        if request.user.is_support:
            # query = Events.objects.filter(support_contact=request.user).values("client", 'client__id')
            query = Events.objects.filter(support_contact=request.user).values("client")
            # query = <QuerySet [{'client': 3}, {'client': 1}]>
            clients = Clients.objects.filter(id__in=query)
            return clients
        return qs.filter(sales_contact=request.user)

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        if request.user.is_admin:
            return True
        if request.user.is_sales:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_admin:
            return True
        if request.user.is_sales:
            return True
        if request.user.is_management:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_admin:
            return True
        if request.user.is_sales:
            return True
        return False


@admin.register(Contracts)
class ContractsAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_admin:
            return qs
        if request.user.is_management:
            return qs
        return qs.filter(sales_contact=request.user)

    def has_view_permission(self, request, obj=None):
        if request.user.is_support:
            return False
        return True

    def has_add_permission(self, request):
        if request.user.is_admin:
            return True
        if request.user.is_sales:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_admin:
            return True
        if request.user.is_sales:
            return True
        if request.user.is_management:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_admin:
            return True
        if request.user.is_sales:
            return True
        return False


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_admin:
            return qs
        if request.user.is_management:
            return qs
        if request.user.is_sales:
            events = Events.objects.filter(client__sales_contact=request.user)
            return events
        return qs.filter(support_contact=request.user)

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        if request.user.is_admin:
            return True
        if request.user.is_sales:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_admin:
            return True
        if request.user.is_sales:
            return True
        return False


@admin.register(EventStatus)
class EventStatusAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        if request.user.is_admin:
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_admin:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_admin:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_admin:
            return True
        return False
