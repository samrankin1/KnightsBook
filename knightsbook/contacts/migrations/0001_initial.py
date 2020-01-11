from django.db import connection, migrations


create_users_sql = 	"""
	CREATE TABLE contacts_users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email VARCHAR(100) UNIQUE NOT NULL,
		password CHAR(32) NOT NULL,
		activated INTEGER NOT NULL DEFAULT 0,
		CHECK (activated in (0, 1))
	)
"""

create_activations_sql = """
	CREATE TABLE contacts_activations (
		token CHAR(36) PRIMARY KEY,
		user INTEGER UNIQUE NOT NULL,
		valid INTEGER NOT NULL DEFAULT 1,
		FOREIGN KEY (user)
			REFERENCES contacts_users(id)
				ON DELETE CASCADE,
		CHECK (valid in (0, 1))
	)
"""

create_contacts_sql = """
	CREATE TABLE contacts_contacts (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		owner INTEGER NOT NULL,
		name_first CHAR(40) NOT NULL,
		name_last CHAR(40) NOT NULL,
		phone_home CHAR(20),
		phone_work CHAR(20),
		addr_street CHAR(40),
		addr_city CHAR(40),
		FOREIGN KEY (owner)
			REFERENCES contacts_users(id)
				ON DELETE CASCADE
	)
"""


def _execute(query):
	with connection.cursor() as cursor:
		cursor.execute(query)


def create_users(apps, schema_editor):
	_execute(create_users_sql)

def create_activations(apps, schema_editor):
	_execute(create_activations_sql)

def create_contacts(apps, schema_editor):
	_execute(create_contacts_sql)


class Migration(migrations.Migration):

	dependencies = [
	]

	operations = [
		migrations.RunPython(create_users),
		migrations.RunPython(create_activations),
		migrations.RunPython(create_contacts),
	]
