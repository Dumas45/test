from typing import TypeVar, Type

T = TypeVar('T')

def validate_type(obj, _type: Type[T]) -> T:
    """
    Validates that the object is of the specified type and returns it.

    Args:
        obj: The object to validate.
        _type: The type to check against.

    Returns:
        The object if it is of the specified type.

    Raises:
        TypeError: If the object is not of the specified type.
    """
    if isinstance(obj, _type):
        return obj
    else:
        raise TypeError(f"Expected object of type {_type}, got {type(obj)}")
