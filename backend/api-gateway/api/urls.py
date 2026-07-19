from django.urls import path

from .views import (
    ContentCollectionView,
    ContentDetailView,
    CsrfTokenView,
    CurrentUserView,
    HealthView,
    LoginView,
    LogoutView,
    RegisterView,
)

urlpatterns = [
    path("health/", HealthView.as_view()),
    path("auth/csrf/", CsrfTokenView.as_view()),
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/me/", CurrentUserView.as_view()),
    path("content/", ContentCollectionView.as_view()),
    path("content/<uuid:content_id>/", ContentDetailView.as_view()),
]
