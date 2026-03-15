from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, SchoolClass, Subject, Lesson, ContactRequest, VisitorLog, Tag, BlogPost

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

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class BlogPostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.title', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    tags_list = TagSerializer(source='tags', many=True, read_only=True)
    thumbnail = serializers.SerializerMethodField()

    def get_thumbnail(self, obj):
        if not obj.thumbnail:
            return None
        return obj.thumbnail.url

    class Meta:
        model = BlogPost
        fields = '__all__'
        extra_kwargs = {
            'slug': {'required': False}
        }

# For the public catalog specialized serializers
class CatalogLessonSerializer(serializers.ModelSerializer):
    youtubeId = serializers.CharField(source='youtube_id')

    class Meta:
        model = Lesson
        fields = ('id', 'slug', 'title', 'youtubeId', 'description', 'duration_seconds', 'order')

class CatalogSubjectSerializer(serializers.ModelSerializer):
    lessons = CatalogLessonSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ('id', 'slug', 'title', 'color', 'lessons', 'order')

class CatalogClassSerializer(serializers.ModelSerializer):
    subjects = CatalogSubjectSerializer(many=True, read_only=True)

    class Meta:
        model = SchoolClass
        fields = ('id', 'slug', 'title', 'subjects', 'order')
