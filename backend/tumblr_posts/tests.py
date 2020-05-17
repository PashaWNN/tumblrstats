import json
from django.test import TestCase


class GetNoteStatistics(TestCase):

    def test_get_note_statistics(self):
        response = self.client.get('/statistics/notes/')
        payload = json.loads(response.body)
        self.assertEquals(payload, [0, 5, 10, 15])
