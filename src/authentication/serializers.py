from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from authentication.models import Users


class UsersSerializer(ModelSerializer):
    """Serialize la classe Users pour la création d'un utilisateur"""
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Users
        fields = ['email', 'first_name', 'last_name', 'password', 'password2', 'is_sales',
                  'is_support', 'is_management']
        # fields = ['email', 'first_name', 'last_name', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # pour s'assurer que password et passorwd2 matchent, on overwrite la méthode save
    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Les mots de passe doivent être identiques'})

        user = Users(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            email=self.validated_data['email'],
            # is_sales=self.validated_data['is_sales'],
            # is_support=self.validated_data['is_support'],
            # is_management=self.validated_data['is_management'],
        )
        user.set_password(self.validated_data['password'])
        print('datas = ', self.validated_data)
        user.save()
        return user
