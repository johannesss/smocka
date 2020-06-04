import os.path

import click

from app.database import db_file_path
from app.database import init_db as init_db_fn


@click.command()
@click.option('--init-db', is_flag=True, help='Initialize the database.')
@click.option('--init-app', is_flag=True, help='Create and migrate db it does not exist).')  # noqa
def run(init_db, init_app):
    if init_db:
        init_db_fn()
        print('init-db: Initialized the database!')
        return

    if init_app:
        if os.path.isfile(db_file_path):
            print('init-app: Database already exists, exiting')
            return

        init_db_fn()
        print('init-app: Initialized the database!')
        return


if __name__ == '__main__':
    run()
