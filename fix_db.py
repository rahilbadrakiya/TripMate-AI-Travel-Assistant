import sqlite3

def fix_db():
    try:
        conn = sqlite3.connect('tripmate.db')
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        if 'name' not in columns:
            print("Adding 'name' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN name VARCHAR")
            
        if 'username' not in columns:
            print("Adding 'username' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN username VARCHAR")
            # Note: SQLite doesn't easily support adding UNIQUE constraints via ALTER TABLE ADD COLUMN
            # but for what we need, just having the column is enough to stop the crash.
            # Uniqueness is enforced by the app logic mostly, and indices can be created.
            
            # Try to create index
            try:
                cursor.execute("CREATE UNIQUE INDEX ix_users_username ON users (username)")
            except Exception as e:
                print(f"Could not create unique index (might already exist or duplicate data): {e}")

        # Update is_verified to 1 (True) for all users since we removed verification
        if 'is_verified' in columns:
             print("Updating is_verified to True for all users...")
             cursor.execute("UPDATE users SET is_verified = 1")

        conn.commit()
        print("Database schema updated successfully.")
        conn.close()
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == "__main__":
    fix_db()
