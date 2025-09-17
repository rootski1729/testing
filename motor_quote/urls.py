from .views import MotorQuoteRequestViewSet, AsyncMotorQuoteRequestViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"request/a", AsyncMotorQuoteRequestViewSet, basename="async-motor-quote-request")
router.register(r"request", MotorQuoteRequestViewSet, basename="motor-quote-request")

urlpatterns = router.urls