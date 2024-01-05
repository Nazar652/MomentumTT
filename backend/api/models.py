from django.db.models import *


class User(Model):
    first_name = TextField()
    surname = TextField(null=True, blank=True)
    username = TextField(null=True, blank=True)
    identifier = IntegerField(unique=True, db_index=True)

    def __str__(self):
        return f'User {self.first_name}. Id: {self.identifier}'


class Account(Model):
    phone_number = CharField(max_length=15, unique=True, db_index=True)
    user = OneToOneField(User, on_delete=CASCADE, to_field='identifier')


class State(Model):
    state = CharField(max_length=20)
    data = TextField(null=True, blank=True)
    user = OneToOneField(User, on_delete=CASCADE, to_field='identifier')
