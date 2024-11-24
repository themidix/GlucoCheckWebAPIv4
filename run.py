#run.py
from app import create_app, db
from dotenv import load_dotenv

app = create_app()
load_dotenv()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
