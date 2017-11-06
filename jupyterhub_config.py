import os
j_location=os.getenv("JUPYTERHUB_LOCATION", '/home/myuser')

c = get_config()
c.JupyterHub.cookie_secret_file = ('{}/jupyterhub_cookie_secret'
									''.format(j_location))
c.JupyterHub.db_url = '{}/jupyterhub.sqlite'.format(j_location)