from rest_framework import routers

from app_skud.api_views import (
    StaffViewSet,
    DepartamentViewSet,
    PositionViewSet,
    CheckpointsViewSet,
    AccessProfileViewSet,
    MonitorCheckAccessViewSet,
)


router = routers.DefaultRouter()
router.register(r"staffs", StaffViewSet)
router.register(r"departaments", DepartamentViewSet)
router.register(r"positions", PositionViewSet)
router.register(r"checkpoints", CheckpointsViewSet)
router.register(r"access_profile", AccessProfileViewSet)
router.register(r"monitor", MonitorCheckAccessViewSet)
