from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import registry, relationship

from allocation.domain import model
from allocation.adapters import repository
import logging
from sqlalchemy import text

metadata = MetaData()
mapper_registry = registry()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderid", String(255)),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255), nullable=False),
    Column("sku", String(255), nullable=False),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", Integer, ForeignKey("order_lines.id")),
    Column("batch_id", Integer, ForeignKey("batches.id")),
)

logger = logging.getLogger(__name__)

def start_mappers():
    """
    Configure SQLAlchemy ORM mappings for domain models.
    
    This function sets up the relationship between:
    - OrderLine objects and the order_lines table
    - Batch objects and the batches table
    - The allocations table that connects them
    """
    lines_mapper = mapper_registry.map_imperatively(
        model.OrderLine, 
        order_lines, 
        properties={
            "_allocations": relationship(
                model.Batch, 
                secondary=allocations, 
                collection_class=set,
                back_populates="_allocations",
                overlaps="_allocations"
            )
        }
    )
    
    batches_mapper = mapper_registry.map_imperatively(
        model.Batch,
        batches,
        properties={
            "_allocations": relationship(
                model.OrderLine, 
                secondary=allocations, 
                collection_class=set,
                back_populates="_allocations",
                overlaps="_allocations"
            )
        },
    )


def clear_mappers():
    """
    Clear all ORM mappings.
    
    This is useful for testing to ensure a clean state between tests.
    """
    mapper_registry.dispose()