from allocation.adapters import repository
from allocation.domain import model
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

def test_repository_can_save_a_batch(session):
    # create a new batch 
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)
    
    # Debug logging
    logger.info(f"Batch reference: {batch.reference}")
    logger.info(f"Batch attributes: {vars(batch)}")
    
    # Create a repo
    repo = repository.SqlAlchemyRepository(session)
    # Add batch to repo
    repo.add(batch)
    # commit to db
    session.commit()

    # Assert that the batch was saved correctly
    rows = session.execute(
        text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"')
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]