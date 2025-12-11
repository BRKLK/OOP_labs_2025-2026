from abc import ABC, abstractmethod
from multiprocessing import reduction
from typing import Any, Self, TypeVar, Generic
from dataclasses import dataclass, field

TEventArgs = TypeVar('TEventArgs')

class EventHandler(ABC, Generic[TEventArgs]):
    @abstractmethod
    def handle(self, sender: object, args: TEventArgs) -> None:
        ...


class EventArgs(ABC):
    ...

@dataclass
class PropertyChangedEventArgs(EventArgs):
    property_name: str

@dataclass
class PropertyChangingEventArgs(EventArgs):
    property_name: str
    old_value: Any
    new_value: Any
    can_change: bool = True


class Event(Generic[TEventArgs]):
    def __init__(self):
        self.handlers: list[EventHandler[TEventArgs]] = []
    
    def __iadd__(self, handler: EventHandler[TEventArgs]) -> Self:
        self.handlers.append(handler)
        return self
    
    def __isub__(self, handler: EventHandler[TEventArgs]) -> Self:
        self.handlers.remove(handler)
        return self

    def invoke(self, sender: object,  args: TEventArgs):
        for handler in self.handlers:
            handler.handle(sender, args)

    __call__ = invoke

class PrintHandler(EventHandler[PropertyChangedEventArgs]):
    def handle(self, sender: object, args: PropertyChangedEventArgs):
        print(f"[{sender}] changed {args.property_name}")

class ValidationHandler(EventHandler[PropertyChangingEventArgs]):
    def handle(self, sender: object, args: PropertyChangingEventArgs):
        if args.new_value == "" or args.property_name.startswith("_") or type(args.new_value) != type(args.old_value):
            args.can_change = False
        else:
            args.can_change = True


class PropertyNotifierMixin:
    def __init__(self):
        self.property_changing = Event[PropertyChangingEventArgs]()
        self.property_changed = Event[PropertyChangedEventArgs]()

    def __setattr__(self, field_name: str, new_value: Any):
        # if not hasattr(self, "property_changing"):
        #     super().__setattr__(field_name, new_value)
        #     return
        if (field_name == "property_changing") or (field_name == "property_changed"):
            super().__setattr__(field_name, new_value)
            return
        
        old_value = getattr(self, field_name, None)

        args_before = PropertyChangingEventArgs(field_name, old_value, new_value)
        self.property_changing(self, args_before)
        if not args_before.can_change:
            return
        
        super().__setattr__(field_name, new_value)

        args_after = PropertyChangedEventArgs(field_name)
        self.property_changed(self, args_after)


class Toad(PropertyNotifierMixin):
    def __init__(self, name: str, address: str, age: int) -> None:
        super().__init__()
        self.name = name
        self.address = address
        self._age = age

        
class Frog(PropertyNotifierMixin):
    def __init__(self, name: str, age: int):
        super().__init__()
        self.name = name
        self.age = age
        

f = Frog("Ferdinand", 45)

f.property_changing += ValidationHandler()
f.property_changed  += PrintHandler()

f.age = 12
f.name = "john"
f.name = ""

t = Toad("nick", '121', 33)

t.property_changing += ValidationHandler()
t.property_changed  += PrintHandler()

t.name = ""
t.name = "roy"
t._age = 22
t._age = 'hello'

