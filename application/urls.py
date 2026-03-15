from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SchoolClassViewSet, SubjectViewSet, 
    LessonViewSet, ContactRequestViewSet, UserViewSet,
    TagViewSet, BlogPostViewSet,
    CatalogAPI, AdminLoginAPI, AnalyticsDashboardAPI, AnalyticsTrackAPI
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'classes', SchoolClassViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'contact-requests', ContactRequestViewSet)
router.register(r'tags', TagViewSet)
router.register(r'blog-posts', BlogPostViewSet)
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/admin-login/', AdminLoginAPI.as_view(), name='admin-login'),
    path('analytics/dashboard/', AnalyticsDashboardAPI.as_view(), name='analytics-dashboard'),
    path('analytics/track/', AnalyticsTrackAPI.as_view(), name='analytics-track'),
    path('public/catalog/', CatalogAPI.as_view(), name='public-catalog'),
    path('', include(router.urls)),
]
