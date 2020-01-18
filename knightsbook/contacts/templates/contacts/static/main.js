function hashpw()
{
	var pass = document.getElementById('password');
	pass.value = md5(pass.value);
	return true;
}
