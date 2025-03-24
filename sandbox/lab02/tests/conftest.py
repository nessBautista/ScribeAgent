import logging
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from allocation.adapters.orm import metadata, start_mappers

@pytest.fixture
def in_memory_db():
    """
    Creates and configures an in-memory SQLite database for testing.
    
    This fixture:
    1. Creates a new SQLAlchemy engine connected to an in-memory SQLite database
    2. Creates all tables defined in the metadata
    3. Returns the engine for other fixtures to use
    
    Using an in-memory database ensures tests are:
    - Fast (no disk I/O)
    - Isolated (each test gets a fresh database)
    - Clean (database is automatically destroyed after test)
    
    Returns:
        SQLAlchemy Engine: Configured database engine
    """

    # If you wanted to create a persistent SQLite database file instead, 
    # you would use a connection string like "sqlite:///path/to/your/database.db".
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine

@pytest.fixture
def session(in_memory_db):
    """
    Provides a SQLAlchemy session for interacting with the test database.
    
    This fixture:
    1. Sets up the ORM mappings between domain models and database tables
    2. Creates a new session connected to the in-memory database
    3. Yields the session to the test
    4. Cleans up by clearing the mappers after the test completes
    
    The session can be used to:
    - Query the database
    - Add/update/delete records
    - Commit transactions
    
    Args:
        in_memory_db: The database engine fixture
        
    Yields:
        SQLAlchemy Session: An active database session
    """
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()

def pytest_configure(config):
    """
    Configures pytest logging settings.
    
    This function:
    1. Sets up basic logging configuration
    2. Sets the log level to INFO
    3. Formats log messages with timestamp, logger name, level, and message
    
    Args:
        config: The pytest configuration object
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
