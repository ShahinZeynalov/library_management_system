from rest_framework import serializers
from library_management_system.library.models import Book, Borrow


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class BorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = '__all__'
        read_only_fields = ['user']  # User field is set automatically by the view

    def create(self, validated_data):
        request = self.context['request']  # Access the request object from the serializer context
        user = request.user  # Retrieve the user from the request
        validated_data['user'] = user  # Add the current user to the validated data
        return super().create(validated_data)