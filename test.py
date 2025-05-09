from api.index import create_app
from dotenv import load_dotenv

if __name__ == '__main__':
    app = create_app()
    load_dotenv()
    app.run(debug=True)