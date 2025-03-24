from dataclasses import dataclass
from datetime import date
from typing import Optional, Set


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    """Represents a batch of inventory with allocation capabilities.
    
    A batch contains a specific quantity of a single SKU (stock keeping unit).
    It can have an optional ETA (estimated time of arrival) date, and tracks
    which order lines are allocated to it.
    
    Attributes:
        ref (str): Unique reference identifier for the batch
        sku (str): Stock keeping unit - product identifier
        eta (Optional[date]): Estimated time of arrival, or None if already available
        _purchased_quantity (int): Total quantity purchased for this batch
        _allocations (Set[OrderLine]): Set of order lines allocated to this batch
    """
    
    def __init__(self, reference: str, sku: str, qty: int, eta: Optional[date] = None):
        """Initialize a new batch.
        
        Args:
            ref: Unique reference identifier for the batch
            sku: Stock keeping unit - product identifier
            qty: Total quantity purchased for this batch
            eta: Estimated time of arrival, or None if already available
        """
        self.reference = reference
        self.sku = sku
        self._purchased_quantity = qty
        self.eta = eta
        self._allocations: Set[OrderLine] = set()  # Type hint to indicate Set of OrderLine objects

    def __repr__(self):
        return f"<Batch: {self.reference}>"

    def __equal__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        
        if other.eta is None:
            return True

        return self.eta > other.eta
    
    def allocate(self, line: OrderLine):
        """Allocate an order line to this batch if possible.
        
        Args:
            line: The order line to allocate
            
        Raises:
            TypeError: If line is not an OrderLine object
        """
        if not isinstance(line, OrderLine):
            raise TypeError(f"Can only allocate OrderLine objects, got {type(line).__name__}")
        
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate_one(self) -> OrderLine:
        """Remove and return a single allocation from this batch.
        
        Returns:
            The order line that was deallocated
        """
        return self._allocations.pop()

    @property
    def allocated_quantity(self) -> int:
        """Calculate the total quantity allocated to this batch.
        
        Returns:
            Sum of quantities from all allocated order lines
        """
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        """Calculate the remaining available quantity in this batch.
        
        Returns:
            The difference between purchased quantity and allocated quantity
        """
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        """Check if an order line can be allocated to this batch.
        
        Args:
            line: The order line to check
            
        Returns:
            True if the SKUs match and there is sufficient available quantity
        """
        return self.sku == line.sku and self.available_quantity >= line.qty

    def change_purchased_quantity(self, qty: int):
        self._purchased_quantity = qty
        while self.available_quantity < 0:
            line = self.deallocate_one()

