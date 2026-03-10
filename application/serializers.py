from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, SchoolClass, Subject, Lesson, ContactRequest, VisitorLog

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
        read_only_fields = ('date_joined',)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class ContactRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = '__all__'

# For the public catalog specialized serializers
class CatalogLessonSerializer(serializers.ModelSerializer):
    youtubeId = serializers.CharField(source='youtube_id')

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'youtubeId', 'description', 'duration_seconds', 'order')

class CatalogSubjectSerializer(serializers.ModelSerializer):
    lessons = CatalogLessonSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ('id', 'title', 'color', 'lessons', 'order')

class CatalogClassSerializer(serializers.ModelSerializer):
    subjects = CatalogSubjectSerializer(many=True, read_only=True)

    class Meta:
        model = SchoolClass
        fields = ('id', 'title', 'subjects', 'order')