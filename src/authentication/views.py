from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from authentication.serializers import UsersSerializer
from crm.permissions import IsUserIsManagementTeam
# Create your views here.


@api_view(['POST', ])
@permission_classes([IsAuthenticated, IsUserIsManagementTeam])
def signup_view(request):

    if request.method == 'POST':
        serializer = UsersSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            data['response'] = 'Nouvel utilisateur enregistré avec succès'
            data['email'] = user.email
            data['first_name'] = user.first_name
            data['last_name'] = user.last_name
            data['is_sales'] = user.is_sales
            data['is_support'] = user.is_support
            data['is_management'] = user.is_management

        else:
            data = serializer.errors
        return Response(data)
