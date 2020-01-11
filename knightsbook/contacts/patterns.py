import re


email_regex = re.compile('^[\w\-\.]+@(?:[\w-]+\.)+[\w-]{2,4}$')

def match_email(email):
	return email_regex.match(email) != None
