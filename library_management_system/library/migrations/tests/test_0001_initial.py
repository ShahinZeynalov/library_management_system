from django.test import TestCase
from library_management_system.library.models import Book, Borrow


class MigrationFileTestCase(TestCase):

    def test_apply_migration(self):

        book_fields = [field.name for field in Book._meta.fields]
        borrow_fields = [field.name for field in Borrow._meta.fields]

        self.assertTrue("title" in book_fields)
        self.assertTrue("author" in book_fields)
        self.assertTrue("availability" in book_fields)
        self.assertTrue("user" in borrow_fields)
        self.assertTrue("book" in borrow_fields)
        self.assertTrue("borrowed_at" in borrow_fields)
        self.assertTrue("due_date" in borrow_fields)
