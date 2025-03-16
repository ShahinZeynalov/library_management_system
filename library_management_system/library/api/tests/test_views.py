from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from library_management_system.library.models import Book, Borrow

User = get_user_model()


class BookViewSetTests(APITestCase):
    def setUp(self):
        # Create a sample book and users
        self.book = Book.objects.create(
            title="Book#1",
            author="Book Author",
            availability=True
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@admin.com', password='adminpass'
        )
        self.normal_user = User.objects.create_user(
            email='user@example.com', password='userpass'
        )
        self.client = APIClient()

    def test_anonymous_user_can_list_books(self):
        # Anonymous user can list books
        response = self.client.get('/api/library/books/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_anonymous_user_cannot_create_books(self):
        # Anonymous user cannot create a book
        response = self.client.post('/api/library/books/', data={
            "title": "New Book",
            "author": "Author",
            "availability": True
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_books(self):
        # Admin user can create a new book
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post('/api/library/books/', data={
            "title": "New Book",
            "author": "Author",
            "availability": True
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_normal_user_cannot_create_books(self):
        # Normal user cannot create a book
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.post('/api/library/books/', data={
            "title": "New Book",
            "author": "Author",
            "availability": True
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_books(self):
        # Admin can update an existing book
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.patch(f'/api/library/books/{self.book.id}/', data={
            "title": "Updated Title"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Title")

    def test_anonymous_user_cannot_delete_books(self):
        # Anonymous user cannot delete a book
        response = self.client.delete(f'/api/library/books/{self.book.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_books(self):
        # Admin user can delete a book
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/library/books/{self.book.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())


class BorrowViewSetTests(APITestCase):
    def setUp(self):
        # Create users and books
        self.user = User.objects.create_user(email="testuser@example.com", password="password")
        self.admin_user = User.objects.create_superuser(email="admin@admin.com", password="adminpass")

        self.available_book = Book.objects.create(
            title="Available Book",
            author="Author 1",
            availability=True,
        )

        self.unavailable_book = Book.objects.create(
            title="Unavailable Book",
            author="Author 2",
            availability=False,
        )

        self.borrow_record = Borrow.objects.create(
            user=self.user,
            book=self.available_book,
            borrowed_at="2023-10-01T10:00:00Z",
            due_date="2023-10-15T10:00:00Z",
        )

        # Create client
        self.client = APIClient()

    # ----------------------
    # PERMISSION TESTS
    # ----------------------

    def test_anonymous_user_cannot_access_borrow_endpoints(self):
        # Anonymous user cannot list borrows
        response = self.client.get("/api/library/borrows/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Anonymous user cannot create a borrow record
        response = self.client.post("/api/library/borrows/", data={"book": self.available_book.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_list_borrow_records(self):
        # Authenticated user can list borrow records
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/library/borrows/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_retrieve_borrow_record(self):
        # Authenticated user can retrieve a specific borrow record
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/library/borrows/{self.borrow_record.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_create_borrow_for_available_book(self):
        # Authenticated user can borrow an available book
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/library/borrows/", data={"book": self.available_book.id, "due_date": "2023-10-20T10:00:00Z"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure the book is now marked as unavailable
        self.available_book.refresh_from_db()
        self.assertFalse(self.available_book.availability)

    def test_authenticated_user_cannot_borrow_unavailable_book(self):
        # Authenticated user cannot borrow an unavailable book
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/library/borrows/", data={"book": self.unavailable_book.id, "due_date": "2023-10-20T10:00:00Z"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "Book is not available for borrowing.")

    def test_authenticated_user_cannot_delete_borrow(self):
        # Authenticated user cannot delete a borrow record
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/library/borrows/{self.borrow_record.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_delete_borrow_record(self):
        # Admin user can delete a borrow record
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f"/api/library/borrows/{self.borrow_record.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Borrow.objects.filter(id=self.borrow_record.id).exists())

    # ----------------------
    # BEHAVIOR TESTS
    # ----------------------

    def test_creating_borrow_marks_book_as_unavailable(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/library/borrows/", data={"book": self.available_book.id, "due_date": "2023-10-31T10:00:00Z"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure the book is now marked as unavailable
        self.available_book.refresh_from_db()
        self.assertFalse(self.available_book.availability)

    def test_creating_borrow_with_nonexistent_book_returns_404(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/library/borrows/", data={"book": 9999, "due_date": "2023-10-20T10:00:00Z"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_due_date_validation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/library/borrows/", data={"book": self.available_book.id, "due_date": "2023-10-31 10:00:00+00:00"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure the borrow record has the correct due date
        borrow = Borrow.objects.get(id=response.data["id"])
        self.assertEqual(str(borrow.due_date), "2023-10-31 10:00:00+00:00")

    # ----------------------
    # EDGE CASE TESTS
    # ----------------------

    def test_cannot_borrow_without_due_date(self):
        # Attempt to borrow a book without providing a due date
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/library/borrows/", data={"book": self.available_book.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_admins_can_update_borrow_record(self):
        # Normal user cannot update a borrow record
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/api/library/borrows/{self.borrow_record.id}/", data={"due_date": "2023-11-01 10:00:00+00:00"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin user can update the borrow record
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/api/library/borrows/{self.borrow_record.id}/", data={"due_date": "2023-11-01 10:00:00+00:00"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the due date was updated
        self.borrow_record.refresh_from_db()
        self.assertEqual(str(self.borrow_record.due_date), "2023-11-01 10:00:00+00:00")