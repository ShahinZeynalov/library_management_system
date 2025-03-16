from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework import status
from library_management_system.library.models import Book, Borrow
from .serializers import BookSerializer, BorrowSerializer
from typing import Sequence

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self) -> Sequence[BasePermission]:
        if self.action in ['list', 'retrieve']:  # Anonymous users can browse books
            permission_classes = [AllowAny]
        elif self.action in ['create', 'update', 'destroy']:  # Admins can manage books
            permission_classes = [IsAdminUser]
        else:  # Default permissions
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrow.objects.all()
    serializer_class = BorrowSerializer

    def get_permissions(self) -> Sequence[BasePermission]:
        if self.action in ['list', 'retrieve', 'create']:  # Only registered users can borrow books
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        book_id = request.data.get('book')
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)


        if book.availability:
            book.availability = False  # Mark book as borrowed
            book.save()

            return super().create(request, *args, **kwargs)
        else:
            return Response({"error": "Book is not available for borrowing."}, status=400)
