install:
	poetry install

build:
	poetry build

package-install:
	python3 -m pip install --user dist/*.whl

uninstall:
	python3 -m pip uninstall blog-0.1.0-py3-none-any.whl

migrations:
	poetry run python3 manage.py makemigrations

migrate:
	poetry run python3 manage.py migrate

collect:
	poetry run python3 manage.py collectstatic

run:
	poetry run python3 manage.py runserver