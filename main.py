import threading

from fastapi import FastAPI
from database.models import models
from database.db_setup import engine
from routers.delivery_api import router as delivery_api
from routers.admin_api import router as admin_api
from setup_update import run_setup_update
app = FastAPI()
models.Base.metadata.create_all(engine)
t1 = threading.Thread(target=run_setup_update.run)
t1.start()

app.include_router(delivery_api)
app.include_router(admin_api)
