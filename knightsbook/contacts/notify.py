from django.contrib import messages


def info(request, message):
	messages.add_message(request, messages.INFO, message)

def error(request, message):
	messages.add_message(request, messages.ERROR, message)
