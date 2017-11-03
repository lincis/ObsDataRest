import json
import pytest
import uuid
import sqlite3
from ObsDataRest import app
source_id = str(uuid.uuid4())

class _TestDataRest:
    def setup_class(self):
        app.testing = True
        self.client = app.test_client()

class TestDataSources(_TestDataRest):
    def teardown_class(self):
        r = self.client.delete('/sources/%s' % (source_id))
        assert r.status_code == 200

    @pytest.mark.first
    def test_source_post(self):
        r = self.client.post('/sources/%s' % (source_id),
            data=json.dumps({ 'Name': 'Test', 'Description': 'Test description' }),
            content_type='application/json')
        assert r.status_code == 200

    def test_source_post2(self):
        with pytest.raises(sqlite3.IntegrityError):
            r = self.client.post('/sources/%s' % (source_id),
                data=json.dumps({ 'Name': 'Test', 'Description': 'Test description' }),
                content_type='application/json')

    @pytest.mark.parametrize('id',('',source_id))
    def test_source_get(self, id):
        r = self.client.get('/sources/%s' % (id),
            content_type='application/json')
        assert r.status_code == 200
        print (r.data)
