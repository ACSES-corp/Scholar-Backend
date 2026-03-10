from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db import models
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate

from .models import Category, SchoolClass, Subject, Lesson, ContactRequest, VisitorLog
from .serializers import (
    UserSerializer, CategorySerializer, SchoolClassSerializer, 
    SubjectSerializer, LessonSerializer, ContactRequestSerializer,
    CatalogClassSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()

class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    permission_classes = [IsAdminUser]
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminUser]
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminUser]
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()

class ContactRequestViewSet(viewsets.ModelViewSet):
    queryset = ContactRequest.objects.all()
    serializer_class = ContactRequestSerializer
    permission_classes = [IsAdminUser]
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

class CatalogAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        classes = SchoolClass.objects.filter(is_active=True)
        serializer = CatalogClassSerializer(classes, many=True)
        return Response({"classes": serializer.data})

class AdminLoginAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user and user.is_staff:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": {
                    "username": user.username,
                    "is_staff": user.is_staff
                }
            })
        return Response({"detail": "Invalid credentials or not a staff member."}, status=401)

class AnalyticsDashboardAPI(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        today = timezone.now().date()
        start_date = today - timedelta(days=days-1)
        
        # Summary
        summary = {
            "range_days": days,
            "unique_visitors": VisitorLog.objects.filter(timestamp__date__gte=start_date).values('ip_address').distinct().count(),
            "total_page_views": VisitorLog.objects.filter(timestamp__date__gte=start_date).count(),
            "total_sessions": VisitorLog.objects.filter(timestamp__date__gte=start_date).values('ip_address', 'user_agent').distinct().count(),
            "returning_visitors": 0, # Simplified
            "total_classes": SchoolClass.objects.count(),
            "total_subjects": Subject.objects.count(),
            "total_lessons": Lesson.objects.count(),
            "total_categories": Category.objects.count(),
            "contact_requests": ContactRequest.objects.filter(status='new').count(),
            "avg_session_depth": 1.5 # Placeholder
        }
        
        # Daily Activity
        activity = VisitorLog.objects.filter(timestamp__date__gte=start_date)\
            .annotate(day=TruncDate('timestamp'))\
            .values('day')\
            .annotate(visits=Count('id'), visitors=Count('ip_address', distinct=True))\
            .order_by('day')
            
        daily_activity = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            # Find in activity
            found = next((item for item in activity if item['day'] == d), None)
            daily_activity.append({
                "day": d.strftime("%Y-%m-%d"),
                "visits": found['visits'] if found else 0,
                "visitors": found['visitors'] if found else 0
            })
            
        # Top Pages
        top_pages = VisitorLog.objects.filter(timestamp__date__gte=start_date)\
            .values('path')\
            .annotate(visits=Count('id'))\
            .order_by('-visits')[:10]
            
        # Top Lessons
        top_lessons = Lesson.objects.order_by('-views_count')[:10].values(
            'title', 'slug', 'views_count', 
            subject_title=models.F('subject__title'),
            class_title=models.F('subject__school_class__title')
        )
        
        # Reformat top_lessons to match frontend
        formatted_lessons = []
        for l in top_lessons:
            formatted_lessons.append({
                "title": l['title'],
                "slug": l['slug'],
                "subject__title": l['subject_title'],
                "subject__school_class__title": l['class_title'],
                "views": l['views_count']
            })

        return Response({
            "summary": summary,
            "top_pages": list(top_pages),
            "daily_activity": daily_activity,
            "event_breakdown": [], # Placeholder
            "high_demand_topics": [], # Placeholder
            "top_lessons": formatted_lessons,
            "class_popularity": [] # Placeholder
        })

class AnalyticsTrackAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        path = request.data.get('path', '')
        event_type = request.data.get('event_type', 'page_view')
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        
        VisitorLog.objects.create(
            ip_address=ip,
            path=path[:255],
            method=request.method,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
        )
        
        # If it's a lesson view, increment its view count
        if event_type == 'lesson_open' or 'lesson' in path:
            # Try to find lesson by slug in path
            parts = [p for p in path.split('/') if p]
            if parts:
                slug = parts[-1]
                Lesson.objects.filter(slug=slug).update(views_count=models.F('views_count') + 1)

        return Response({"status": "ok"})

from django.contrib.auth.models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
