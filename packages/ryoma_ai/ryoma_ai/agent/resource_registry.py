import weakref
from collections import defaultdict
from typing import Any, Dict, List, Optional, Type, TypeVar

T = TypeVar("T")


class ResourceRegistry:
    """
    A lightweight registry for tracking arbitrary Python objects (resources)
    by their memory ID, type, and optionally a human-readable name.

    It uses weak references to avoid memory leaks and allows retrieval by:
        - object ID (via `id(obj)`)
        - object type (class)
    """

    def __init__(self):
        # Stores resources by Python's id(obj), using weak references.
        self._by_id: weakref.WeakValueDictionary[int, Any] = weakref.WeakValueDictionary()

        # Stores lists of resources by their type.
        self._by_type: defaultdict[type, List[Any]] = defaultdict(list)

        # Optional: stores a mapping of custom names to object IDs.
        self._name_to_id: Dict[str, int] = {}

    def register(self,
                 obj: Any,
                 name: Optional[str] = None) -> int:
        """
        Register an object in the registry.

        Args:
            obj: The object to register.
            name: Optional custom name for the object (e.g., "my_dataframe").

        Returns:
            The unique `id()` of the object.
        """
        obj_id = id(obj)
        self._by_id[obj_id] = obj
        self._by_type[type(obj)].append(obj)

        if name:
            self._name_to_id[name] = obj_id

        return obj_id

    def get_by_id(self,
                  obj_id: int) -> Optional[Any]:
        """
        Retrieve an object by its id().

        Args:
            obj_id: The object's id().

        Returns:
            The object if still alive, else None.
        """
        return self._by_id.get(obj_id)

    def get_by_type(self,
                    cls: Type[T]) -> List[T]:
        """
        Retrieve all objects of a given type.

        Args:
            cls: The class/type to filter by.

        Returns:
            List of matching objects.
        """
        return self._by_type.get(cls, [])

    def get_by_name(self,
                    name: str) -> Optional[Any]:
        """
        Retrieve a resource by its assigned name.

        Args:
            name: The custom name of the object.

        Returns:
            The object if registered and alive, else None.
        """
        obj_id = self._name_to_id.get(name)
        return self._by_id.get(obj_id) if obj_id else None

    def list_ids(self) -> List[int]:
        """
        List all currently tracked object IDs.
        """
        return list(self._by_id.keys())

    def list_all(self) -> List[Any]:
        """
        List all currently tracked objects.
        """
        return list(self._by_id.values())

    def list_names(self) -> List[str]:
        """
        List all named resource keys.
        """
        return list(self._name_to_id.keys())
