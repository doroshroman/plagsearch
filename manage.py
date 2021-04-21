from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import app, db
from web.models import Role, RoleName


cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("Tables are created")

@cli.command("seed_db")
def seed_db():
    role_names = [r for r in RoleName]
    roles = [db.session.add(Role(name=_name)) for _name in role_names]
    db.session.commit()
    print("Populated user roles")

if __name__ == "__main__":
    cli()

