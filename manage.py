import click

from app.database import init_db as init_db_fn


@click.command()
@click.option('--init-db', is_flag=True, help='Initialize the database.')
def execute(init_db):
    if init_db:
        init_db_fn()
        print('Initialized the database!')


if __name__ == '__main__':
    execute()
