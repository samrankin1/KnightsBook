import json
import uuid

from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse

from . import db, mail, notify, patterns


def home():
	return redirect('contacts:index')

def jsonRedirect(view, args=None):
	return JsonResponse(
		{'redirect': reverse(view, args=args)}
	)

def jsonRedirectHome():
	return jsonRedirect('contacts:index')


def index(request):
	if not 'user' in request.session:
		# notify.info(request, 'You are NOT logged in')
		return render(request, 'contacts/login.html')

	else:
		user = request.session['user']
		# notify.info(request, "You are logged in as '" + str(db.get_email(user)) + "'")
		return redirect('contacts:contacts')

def register(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		email, password = params.get('email'), params.get('password')

		if not email or not password:
			return HttpResponseBadRequest("Fields 'email' and 'password' are required")

		elif not patterns.match_email(email):
			notify.error(request, 'Invalid email address!')

		elif db.check_email_exists(email):
			notify.error(request, 'User already exists!')

		else:
			# notify.info(request, "Register Email = '" + email + "', Password = '" + password + "'")
			db.insert_user(email, password)

			token = str(uuid.uuid4())
			db.insert_activation(email, token)
			mail.send_activation_mail(request, email, token)

			notify.info(request, "Activation code sent to '" + email + "'")

		return jsonRedirectHome()

	return render(request, 'contacts/register.html')

def activate(request, token):
	# notify.info(request, "Activate Token = '" + token + "'")

	row = db.get_activation(token)
	if not row:
		return HttpResponseBadRequest('Invalid activation token!')

	user, valid = row

	if not valid:
		notify.info(request, 'Your account is already activated')
	else:
		db.activate_user(user)
		db.invalidate_activation(token)
		notify.info(request, "Successfuly verified '" + str(db.get_email(user)) + "'")

	return home()

def login(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		email, password = params.get('email'), params.get('password')

		if not email or not password:
			return HttpResponseBadRequest("Fields 'email' and 'password' are required")

		# notify.info(request, "Login Email = '" + email + "', Password = '" + password + "'")

		row = db.get_login(email)

		if not row:
			notify.error(request, 'User does not exist')
			return jsonRedirectHome()

		user, pass_hash, activated = row

		if activated != 1:
			notify.error(request, 'Account is not activated! Check your email')

		elif password != pass_hash:
			notify.error(request, 'Wrong password!')

		else:
			request.session['user'] = user
			# notify.info(request, "Successful login as '" + email + "'")

		return jsonRedirectHome()

	return home()


def logout(request):
	if 'user' in request.session:
		del request.session['user']

	return home()


def contacts(request):
	if not 'user' in request.session:
		notify.info(request, 'You must be logged in to view your contacts')
		return render(request, 'contacts/login.html')

	user = request.session['user']

	# Load user's contacts and pass them to template
	search = request.GET.get('search')
	contacts = db.get_user_contacts(user, search)

	return render(request, 'contacts/contacts.html',
		{'search': search, 'contacts': contacts})

def create(request):
	if not 'user' in request.session:
		notify.info(request, 'You must be logged in to create a contact')
		return render(request, 'contacts/login.html')

	user = request.session['user']

	if request.method == 'POST':
		params = json.loads(request.body)
		name_first = params.get('name_first')
		name_last = params.get('name_last')
		phone_home = params.get('phone_home')
		phone_work = params.get('phone_work')
		addr_street = params.get('addr_street')
		addr_city = params.get('addr_city')
		ucf_major = params.get('ucf_major')
		ucf_graduation = params.get('ucf_graduation')
		ucf_role = params.get('ucf_role')

		if not name_first or not name_last:
			return HttpResponseBadRequest("Fields 'name_first' and 'name_last' are required")

		db.insert_contact(user, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role)
		notify.info(request, "Created contact '" + name_first + " " + name_last + "'")

		return jsonRedirectHome()

	return render(request, 'contacts/create.html')

def contact(request, contact_id):
	if not 'user' in request.session:
		notify.info(request, 'You must be logged in to view a contact')
		return render(request, 'contacts/login.html')

	user = request.session['user']
	contact = db.get_contact(contact_id)

	if not contact:
		return HttpResponseNotFound('Contact not found')

	owner, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role = contact

	if owner != user:
		return HttpResponseBadRequest('You are not authorized to view this contact')
	else:
		return render(request, 'contacts/contact.html',
			{'id': contact_id, 'name_first': name_first, 'name_last': name_last, 'phone_home': phone_home,
			'phone_work': phone_work, 'addr_street': addr_street, 'addr_city': addr_city,
			'ucf_major': ucf_major, 'ucf_graduation': ucf_graduation, 'ucf_role': ucf_role})

def contactJSON(request, contact_id):
	if not 'user' in request.session:
		return HttpResponseBadRequest('You are not authorized to view this contact')

	user = request.session['user']
	contact = db.get_contact(contact_id)

	if not contact:
		return HttpResponseNotFound('Contact not found')

	owner, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role = contact

	if owner != user:
		return HttpResponseBadRequest('You are not authorized to view this contact')
	else:
		return JsonResponse({
			'id': contact_id, 'name_first': name_first, 'name_last': name_last,
			'phone_home': phone_home, 'phone_work': phone_work, 'addr_street': addr_street, 'addr_city': addr_city,
			'ucf_major': ucf_major, 'ucf_graduation': ucf_graduation, 'ucf_role': ucf_role
		})

def edit(request, contact_id):
	if not 'user' in request.session:
		notify.info(request, 'You must be logged in to edit a contact')
		return render(request, 'contacts/login.html')

	user = request.session['user']
	contact = db.get_contact(contact_id)

	if not contact:
		return HttpResponseNotFound('Contact not found')

	owner, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role = contact

	if owner != user:
		return HttpResponseBadRequest('You are not authorized to edit this contact')

	if request.method == 'POST':
		params = json.loads(request.body)
		name_first = params.get('name_first')
		name_last = params.get('name_last')
		phone_home = params.get('phone_home')
		phone_work = params.get('phone_work')
		addr_street = params.get('addr_street')
		addr_city = params.get('addr_city')
		ucf_major = params.get('ucf_major')
		ucf_graduation = params.get('ucf_graduation')
		ucf_role = params.get('ucf_role')

		if not name_first or not name_last:
			return HttpResponseBadRequest("Fields 'name_first' and 'name_last' are required")

		db.update_contact(contact_id, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role)
		notify.info(request, "Updated contact '" + name_first + " " + name_last + "'")
		return jsonRedirect('contacts:contacts')


	return render(request, 'contacts/edit.html',
		{'id': contact_id, 'name_first': name_first, 'name_last': name_last, 'phone_home': phone_home,
		'phone_work': phone_work, 'addr_street': addr_street, 'addr_city': addr_city,
		'ucf_major': ucf_major, 'ucf_graduation': ucf_graduation, 'ucf_role': ucf_role})

def delete(request, contact_id):
	if not 'user' in request.session:
		notify.info(request, 'You must be logged in to delete a contact')
		return render(request, 'contacts/login.html')

	user = request.session['user']
	contact = db.get_contact(contact_id)

	if not contact:
		return HttpResponseNotFound('Contact not found')

	owner, name_first, name_last, phone_home, phone_work, addr_street, addr_city, ucf_major, ucf_graduation, ucf_role = contact

	if owner != user:
		return HttpResponseBadRequest('You are not authorized to delete this contact')

	if request.method == 'POST':
		params = request.POST

		if params.get('confirm'):
			db.delete_contact(contact_id)
			notify.info(request, "Deleted contact '" + name_first + " " + name_last + "'")
		return home()

	else:
		return render(request, 'contacts/delete.html',
			{'id': contact_id, 'name_first': name_first, 'name_last': name_last, 'phone_home': phone_home,
			'phone_work': phone_work, 'addr_street': addr_street, 'addr_city': addr_city,
			'ucf_major': ucf_major, 'ucf_graduation': ucf_graduation, 'ucf_role': ucf_role})
