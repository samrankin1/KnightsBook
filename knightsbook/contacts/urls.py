from django.urls import path, re_path

from . import views


app_name = 'contacts'

urlpatterns = [
	path('', views.index, name='index'),

	path('register/', views.register, name='register'),
	re_path(r'activate/(?P<token>[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12})',
		views.activate, name='activate'), # Takes activation token (UUIDv4)
	path('login/', views.login, name='login'),
	path('logout/', views.logout, name='logout'),

	path('contacts/', views.contacts, name='contacts'),
	path('create/', views.create, name='create'),
	re_path(r'contacts/(?P<contact_id>\d+)$', views.contact, name='contact'),
	re_path(r'contacts/(?P<contact_id>\d+)/json$', views.contactJSON, name='contactJSON'),
	re_path(r'contacts/(?P<contact_id>\d+)/edit$', views.edit, name='edit'),
	re_path(r'contacts/(?P<contact_id>\d+)/delete$', views.delete, name='delete'),
]
