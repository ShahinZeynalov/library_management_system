from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from library_management_system.library.api.views import BookViewSet, BorrowViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("books", BookViewSet)
router.register("borrows", BorrowViewSet)


app_name = "library" 
urlpatterns = router.urls
