from datetime import date
from allocation.domain.model import Batch, OrderLine
import pytest


def test_batch_instantiation():
    # Arrange: Create a Batch with sample values.
    ref = "batch-001"
    sku = "PRODUCT-XYZ"
    qty = 100
    eta = date.today()

    
    # Act: Instantiate the Batch.
    batch = Batch(reference=ref, sku=sku, qty=qty, eta=eta)
    
    # Assert: Verify that attributes are set correctly.
    assert batch.reference == ref
    assert batch.sku == sku
    # If your Batch doesn't expose a public purchased_qty attribute,
    # you may check the internal state directly if acceptable in your testing context.
    assert batch._purchased_quantity == qty
    assert batch.eta == eta
    # Ensure that the allocations set is empty upon instantiation.
    assert batch._allocations == set()
    

def test_batch_representation():
    batch = Batch(reference="batch-001", sku="product-xyz", qty=10, eta = date.today())
    assert batch.__repr__() == "<Batch: batch-001>"

def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty),
    )

def test_allocate_rejects_non_orderline_objects():
    # Arrange
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    not_an_order_line = "not an OrderLine"
    
    # Act & Assert
    with pytest.raises(TypeError, match="Can only allocate OrderLine objects"):
        batch.allocate(not_an_order_line)
    
    # Verify the batch's allocations remain empty
    assert batch.available_quantity == 20
    assert batch._allocations == set()


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18

def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False


def test_changing_batch_quantity_deallocates_lines_if_necessary():
    # Arrange: Create a batch with 20 units and allocate 2 order lines
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line1 = OrderLine("order-1", "SMALL-TABLE", 10)
    line2 = OrderLine("order-2", "SMALL-TABLE", 8)
    
    # Allocate both lines
    batch.allocate(line1)
    batch.allocate(line2)
    assert batch.available_quantity == 2
    
    # Act: Reduce the purchased quantity to 15
    batch.change_purchased_quantity(15)
    
    # Assert: One line should have been deallocated
    # Available quantity should be non-negative
    assert batch.available_quantity >= 0
    # Only one line should remain allocated
    assert len(batch._allocations) == 1
    # The total allocated quantity should be less than or equal to 15
    assert batch.allocated_quantity <= 15


def test_changing_batch_quantity_doesnt_deallocate_if_not_needed():
    # Arrange: Create a batch with 20 units and allocate 1 order line
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-1", "SMALL-TABLE", 10)
    
    batch.allocate(line)
    assert batch.available_quantity == 10
    
    # Act: Reduce the purchased quantity but not enough to require deallocation
    batch.change_purchased_quantity(15)
    
    # Assert: The line should still be allocated
    assert batch.available_quantity == 5
    assert len(batch._allocations) == 1
    assert line in batch._allocations

