from .models import (
    Students, CustomUser, Subjects, StudentResult)
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


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['id', 'name']

class StudentResultSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)  
    class Meta:
        model = StudentResult
        fields = ['student_id', 'subject_id', 'subject', 'subject_exam_marks', 'subject_assignment_marks']