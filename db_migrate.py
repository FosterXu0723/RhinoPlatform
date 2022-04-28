"""
@File: db_migrate.py
@author: guoweiliang
@date: 2021/5/20
"""
from app import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = create_app()

Migrate(app=app, db=db, compare_type=True, compare_server_default=True)

manager = Manager(app)
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
