import abc
from allocation.domain import model

class AbstractRepository(abc.ABC):
    """
    Abstract base class defining the repository interface.
    
    This class follows the Repository pattern, providing a collection-like
    interface for accessing domain objects while abstracting away the
    details of database access.
    
    All concrete repository implementations must inherit from this class
    and implement its abstract methods.
    """
    
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        """
        Add a new batch to the repository.
        
        Args:
            batch: The Batch object to add to the repository
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        """
        Retrieve a batch by its reference.
        
        Args:
            reference: The unique reference identifier for the batch
            
        Returns:
            model.Batch: The requested batch
            
        Raises:
            Exception: If the batch cannot be found
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """
    SQLAlchemy implementation of the batch repository.
    
    This class uses SQLAlchemy ORM to persist and retrieve Batch
    objects from a relational database.
    """
    
    def __init__(self, session):
        """
        Initialize the repository with a SQLAlchemy session.
        
        Args:
            session: An active SQLAlchemy session
        """
        self.session = session

    def add(self, batch):
        """
        Add a batch to the database.
        
        Args:
            batch: The Batch object to add
        """
        self.session.add(batch)

    def get(self, reference):
        """
        Get a batch by reference from the database.
        
        Args:
            reference: The batch reference to look up
            
        Returns:
            model.Batch: The requested batch
            
        Raises:
            sqlalchemy.orm.exc.NoResultFound: If the batch doesn't exist
        """
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        """
        List all batches in the database.
        
        Returns:
            list[model.Batch]: A list of all Batch objects
        """
        return self.session.query(model.Batch).all()
