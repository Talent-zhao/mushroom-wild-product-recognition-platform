import os
if os.path.exists('requirements.txt'):
    os.remove('requirements.txt')

os.system('pip freeze > requirements-all.txt')
os.system('python -m pigar generate')


