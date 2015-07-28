import pytest

from pymongo import errors

from flask_blog import db, init_db, drop_db, models


class TestDatabaseConnections():

    def test_db_connection(self, mongodb):
        assert mongodb['client'].server_info()['ok']

    def test_db_connection_with_app(self, mongodb, app, app_ctx):
        assert db.client.server_info()['ok']
        assert '27027' in str(db.client)

    def test_db_init_drop(self, mongodb, app, app_ctx):
        init_db()
        assert 'users' in db.collection_names()

        drop_db()
        assert 'test_db' not in db.client.database_names()
        assert len(db.client.database_names()) == 2

    @pytest.fixture
    def johndoe_user(self, app, ctx, mongodb_inited):
        user = models.Users.add(name='John Doe', email='jd@example.com')
        return str(user._id)

    def test_add_user_in_collection(self, johndoe_user):
        collection = models.MongoUser._get_collection()
        assert collection.find_one({'name': 'John Doe'})

    def test_user_with_same_email(self, johndoe_user):
        with pytest.raises(errors.DuplicateKeyError):
            models.Users.add(name='Jake Doe', email='jd@example.com')

    def test_get_user_from_email(self, johndoe_user):
        assert models.Users.from_email('jd@example.com')

    def test_get_user_from_username_or_email(self, johndoe_user):
        assert models.Users.from_username_or_email('jd@example.com')

    def test_get_user_from_id(self, johndoe_user):
        assert models.Users.from_id(johndoe_user)

# vim:set ft=python sw=4 et spell spelllang=en:
