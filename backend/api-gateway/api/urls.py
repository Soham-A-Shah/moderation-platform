from django.urls import path

from .views import ContentCollectionView, ContentDetailView, HealthView

urlpatterns = [
    path("health/", HealthView.as_view()),
    path("content/", ContentCollectionView.as_view()),
    path("content/<uuid:content_id>/", ContentDetailView.as_view()),
]
