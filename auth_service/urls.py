from django.urls import path

from auth_service.views import UpdateUserSignalApiView

urlpatterns = [
    path('sysapi/update-signal/', UpdateUserSignalApiView.as_view(), name='update-signal')
]
