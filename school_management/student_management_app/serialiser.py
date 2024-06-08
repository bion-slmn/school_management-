from .models import Students, CustomUser
from rest_framework import serializers



class StudentSerialiser(serializers.Serializer):
    class Meta:
        model = Students
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'
        read_only_fields = ("last_login", "date_joined")

    def create(self, validated_data):
        # Handle password hashing here
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user