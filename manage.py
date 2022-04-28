from app import create_app, scheduler
from config import Config

# app.run(host='127.16.0.235', port=80)

# ## local

app = create_app()

scheduler.start()

