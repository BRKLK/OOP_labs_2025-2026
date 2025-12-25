from abc import ABC, abstractmethod
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
        

def run_test(description: str, target_obj: Any, attr_name: str, value_to_set: Any, should_succeed: bool):
    print(f"\nTEST: {description}")
    print("-" * 60)
    
    # 1. Запоминаем старое значение
    old_val = getattr(target_obj, attr_name)
    print(f"Context: {target_obj}")
    print(f"Action : Set '{attr_name}' to {value_to_set!r}")
    
    # 2. Пытаемся изменить
    setattr(target_obj, attr_name, value_to_set)
    
    # 3. Проверяем новое значение
    new_val = getattr(target_obj, attr_name)
    
    # 4. Оценка результата
    change_happened = (new_val == value_to_set)
    
    if should_succeed:
        if change_happened:
            print(f"RESULT : SUCCESS (Value updated to {new_val!r})")
        else:
            print(f"RESULT : FAILED (Expected update, but value remained {new_val!r})")
    else:
        if not change_happened and new_val == old_val:
            print(f"RESULT : SUCCESS (Change correctly blocked, value is still {new_val!r})")
        else:
            print(f"RESULT : FAILED (Expected block, but value changed to {new_val!r})")
    print("-" * 60)


# --- ЗАПУСК ТЕСТОВ ---

if __name__ == "__main__":
    print("=== STARTING APPLICATION TESTS ===\n")

    # 1. Настройка Frog
    f = Frog("Ferdinand", 45)
    f.property_changing += ValidationHandler()
    f.property_changed  += PrintHandler()

    # Тест 1: Валидное изменение числа
    run_test(
        description="Frog: Valid age update",
        target_obj=f, 
        attr_name="age", 
        value_to_set=12, 
        should_succeed=True
    )

    # Тест 2: Валидное изменение имени
    run_test(
        description="Frog: Valid name update",
        target_obj=f,
        attr_name="name",
        value_to_set="John",
        should_succeed=True
    )

    # Тест 3: Невалидное имя (пустая строка)
    run_test(
        description="Frog: Invalid name (Empty string rule)",
        target_obj=f,
        attr_name="name",
        value_to_set="",
        should_succeed=False
    )

    # Тест 4: Невалидный тип данных
    run_test(
        description="Frog: Invalid type (String assigned to Int)",
        target_obj=f,
        attr_name="age",
        value_to_set="Too Old",
        should_succeed=False
    )

    print("\n" + "="*30 + "\n")

    # 2. Настройка Toad
    t = Toad("Nick", '121 Swamp Ln', 33)
    t.property_changing += ValidationHandler()
    t.property_changed  += PrintHandler()

    # Тест 5: Попытка изменения поля с подчеркиванием
    run_test(
        description="Toad: Private attribute modification",
        target_obj=t,
        attr_name="_age",
        value_to_set=22,
        should_succeed=False
    )

    # Тест 6: Попытка изменения поля с подчеркиванием + неверный тип
    run_test(
        description="Toad: Private attribute + Wrong Type",
        target_obj=t,
        attr_name="_age",
        value_to_set='hello',
        should_succeed=False
    )
    
    # Тест 7: Успешное изменение обычного поля у Toad
    run_test(
        description="Toad: Valid name change",
        target_obj=t,
        attr_name="name",
        value_to_set="Roy",
        should_succeed=True
    )
