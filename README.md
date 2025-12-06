# Artlog Backend

- A full-stack web application for managing artists, artworks, and exhibitions. Built with FastAPI (Python) backend and React (JavaScript) frontend.

## Set-up

- Install depedencies
`pipenv install sqlalchemy alembic "fastapi[standard]"`

- Activate virtual environment
`pipenv shell`

- Initialize migrations
`alembic init migration`

- Update alembic.ini file
- create necessary files
- modify env.py

## Handling migrations

- Generate a migration
`alembic revision --autogenerate -m"first migration"`

- Apply migration
`alembic upgrade head`
- Create a connection

## Author 
Joyce Njogu

## License
MIT


