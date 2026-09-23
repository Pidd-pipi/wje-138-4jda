from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from fleet_app.views.dispatch_views import dispatch_orders
from fleet_app.views.driver_views import drivers
from fleet_app.views.fuel_views import fuel_records
from fleet_app.views.maintenance_views import (
    maintenance_complete,
    maintenance_records,
    maintenance_start,
)
from fleet_app.views.vehicle_dispatch_views import vehicle_dispatch_check
from fleet_app.views.vehicle_views import vehicles


@api_view(['GET'])
def health(request):
    return Response({'status': 'ok', 'service': 'fleet-dispatch'})


urlpatterns = [
    path('health/', health),
    path('vehicles/', vehicles),
    path('vehicles/<int:vehicle_id>/dispatch-check/', vehicle_dispatch_check),
    path('drivers/', drivers),
    path('dispatch-orders/', dispatch_orders),
    path('maintenance-records/', maintenance_records),
    path('maintenance-records/<int:record_id>/start/', maintenance_start),
    path('maintenance-records/<int:record_id>/complete/', maintenance_complete),
    path('fuel-records/', fuel_records),
]
