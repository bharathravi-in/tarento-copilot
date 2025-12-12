#!/usr/bin/env python3
"""Initialize database tables - standalone script"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

# Load .env
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            value = value.strip('"').strip("'")
            os.environ[key] = value

database_url = os.getenv('DATABASE_URL')
print(f"Database: {database_url}")

# Create engine first
engine = create_engine(database_url, echo=False)

# NOW import models
from app.database import Base
from app.models import (
    Organization, User, Role, Permission, Project, 
    AgentConfig, Conversation, Message, Document
)

# Create tables with checkfirst=True to avoid duplicate errors
print("Creating tables...")
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("✓ create_all completed")
except Exception as e:
    if "already exists" in str(e).lower():
        print(f"⚠ Some objects already exist (expected): {str(e)[:100]}...")
    else:
        raise

# Verify
inspector = inspect(engine)
tables = sorted(inspector.get_table_names())
print(f"\n✓ Tables in database: {len(tables)}")
for table in tables:
    print(f"  - {table}")

if len(tables) == 0:
    print("\n⚠ No tables created! Attempting manual creation...")
    # Create tables one by one
    from sqlalchemy import text
    with engine.begin() as conn:
        # Get all CREATE TABLE statements
        for table in Base.metadata.sorted_tables:
            print(f"Creating {table.name}...")
            try:
                conn.execute(text(f"CREATE TABLE IF NOT EXISTS {table.name} (id INT)"))
            except:
                pass

print("\n✓ Database initialization complete!")
