from .views import MotorPolicyViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"policy", MotorPolicyViewSet, basename="motor-policy")

urlpatterns = router.urls