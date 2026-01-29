import models
from database import engine

print("Creating database tables...")
models.Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
print("Verifying ChatMessage table...")
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
if "chat_messages" in tables:
    print("SUCCESS: chat_messages table exists.")
else:
    print("FAILURE: chat_messages table was NOT created.")
