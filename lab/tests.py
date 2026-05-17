from django.test import TestCase


class LabViewsTestCase(TestCase):
    """Test cases for Goshen Laboratory views."""

    def test_index_page_loads(self):
        """Test that laboratory index page loads."""
        response = self.client.get('/lab/')
        self.assertEqual(response.status_code, 200)
