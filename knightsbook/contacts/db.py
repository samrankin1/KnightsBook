from django.db import connection


def _execute(query, values=None):
	with connection.cursor() as cursor:
		cursor.execute(query, values)

def _fetchone(query, values=None):
	with connection.cursor() as cursor:
		cursor.execute(query, values)
		return cursor.fetchone()

def _fetchall(query, values=None):
	with connection.cursor() as cursor:
		cursor.execute(query, values)
		return cursor.fetchall()


# User queries

insert_user_sql = """
	INSERT INTO contacts_users (email, password)
	VALUES (%s, %s)
"""

activate_user_sql = """
	UPDATE contacts_users SET activated = 1
	WHERE id = %s
"""

email_exists_sql = """
	SELECT COUNT(*) FROM contacts_users
	WHERE email = %s
"""

user_by_email_sql = """
	SELECT id, password, activated FROM contacts_users
	WHERE email = %s
"""

email_by_id_sql = """
	SELECT email FROM contacts_users
	WHERE id = %s
"""

def insert_user(email, password):
	_execute(
		insert_user_sql,
		(email, password)
	)

def activate_user(user):
	_execute(
		activate_user_sql,
		(user, )
	)

def check_email_exists(email):
	row = _fetchone(
		email_exists_sql,
		(email, )
	)

	if not row:
		# A count should always be returned
		return True
	else:
		return row[0] == 1

def get_login(email):
	return _fetchone(
		user_by_email_sql,
		(email, )
	)

def get_email(user):
	row = _fetchone(
		email_by_id_sql,
		(user, )
	)

	if not row:
		return None
	else:
		return row[0]


# Activation queries

insert_activation_sql = """
	INSERT INTO contacts_activations (token, user)
	VALUES (
		%s,
		(SELECT id FROM contacts_users WHERE email = %s)
	)
"""

activation_invalidate_sql = """
	UPDATE contacts_activations SET valid = 0
	WHERE token = %s
"""

activation_token_sql = """
	SELECT user, valid FROM contacts_activations
	WHERE token = %s
"""

def insert_activation(email, token):
	_execute(
		insert_activation_sql,
		(token, email)
	)

def invalidate_activation(token):
	_execute(
		activation_invalidate_sql,
		(token, )
	)

def get_activation(token):
	row = _fetchone(
		activation_token_sql,
		(token, )
	)

	if not row:
		return None
	else:
		return (row[0], row[1] == 1)


# Contact queries

insert_contact_sql = """
	INSERT INTO contacts_contacts (owner, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role)
	VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

contact_by_id_sql = """
	SELECT owner, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role
	FROM contacts_contacts
	WHERE id = %s
"""

contacts_by_owner_sql = """
	SELECT id, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role
	FROM contacts_contacts
	WHERE owner = %s
"""

contacts_by_owner_filtered_sql = """
	SELECT id, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role
	FROM contacts_contacts
	WHERE owner = %s AND CONCAT(name_first, ' ', name_last) LIKE %s
"""

contact_update_sql = """
	UPDATE contacts_contacts
	SET name_first = %s, name_last = %s, phone_home = %s, phone_work = %s, addr_street = %s, addr_city = %s, ucf_major = %s, ucf_graduation = %s, ucf_role = %s
	WHERE id = %s
"""

contact_delete_sql = """
	DELETE FROM contacts_contacts
	WHERE id = %s
"""

def insert_contact(owner, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role):
	_execute(
		insert_contact_sql,
		(owner, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role)
	)

def get_contact(contact):
	return _fetchone(
		contact_by_id_sql,
		(contact, )
	)

def get_user_contacts(user, search=None):
	if search:
		return _fetchall(
			contacts_by_owner_filtered_sql,
			(user, '%' + search + '%')
		)
	else:
		return _fetchall(
			contacts_by_owner_sql,
			(user, )
		)

def update_contact(contact, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role):
	_execute(
		contact_update_sql,
		(name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role, contact)
	)

def delete_contact(contact):
	_execute(
		contact_delete_sql,
		(contact, )
	)
