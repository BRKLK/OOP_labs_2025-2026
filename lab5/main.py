from token import OP
from typing import Any, Self, Optional, TypeVar, Generic, Sequence
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
# import json
from pathlib import Path
import os
import pickle


T = TypeVar("T")


@dataclass
class User:
    id: int
    name: str
    login: str
    password: str
    email: Optional[str] = None
    address: Optional[str] = None

    def __repr__(self) -> str:
        parts = [
            f"id: {self.id}",
            f"name: {self.name}",
            f"login: {self.login}",
        ]
        if self.email is not None:
            parts.append(f"email: {self.email}")
        if self.address is not None:
            parts.append(f"address: {self.address}")
        return "\n".join(parts)

    def __lt__(self, other: Self) -> bool:
        return self.name < other.name
    

class IDataRepository(ABC, Generic[T]):
    @abstractmethod
    def get_all(self) -> Sequence[T]:
        ...

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        ...

    @abstractmethod
    def add(self, item: T) -> None:
        ...

    @abstractmethod
    def update(self, item: T) -> None:
        ...

    @abstractmethod
    def delete(self, item: T) -> None:
        ...


class IUserRepository(IDataRepository[User]):
    @abstractmethod
    def get_by_login(self, login: str) -> Optional[User]:
        ...


class FileDataRepository(IDataRepository[T]):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self._data: list[T] = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.file_path):
            return []
        else:
            with open(self.file_path, "rb") as f:
                return pickle.load(f)
    
    def _save_data(self):
        with open(self.file_path, 'wb') as f:
            pickle.dump(self._data, f)

    def get_all(self):
        return self._data

    def get_by_id(self, id: int) -> Optional[T]:
        for item in self._data:
            if item.id == id:
                return item
        return None
    
    def add(self, item: T) -> None:
        self._data.append(item)
        self._save_data()

    def update(self, item: T) -> None:
        # if item.id == None:
        #     print("")

        for i, updatable_item in enumerate(self._data):
            if updatable_item.id == item.id:
                self._data[i] = item
                self._save_data()
                return
        else:
            print(f"Item with id {item.id} not found")
    
    def delete(self, item: T) -> None:
        target_id = item.id
        self._data = [item for item in self._data if item.id != target_id]
        self._save_data()


class FileUserRepository(FileDataRepository[User], IUserRepository):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
    
    def get_by_login(self, login: str) -> User:
        for user in self._data:
            if user.login == login:
                return user
        return None


class IAuthService(ABC):
    @property
    @abstractmethod
    def current_user(self)  -> Optional[User]:
        ...

    @abstractmethod
    def sign_in(self, user: User) -> None:
        ...

    @abstractmethod
    def sign_out(self, user: User) -> None:
        ...

    @property
    @abstractmethod
    def is_authorized(self) -> bool:
        ...


class FileAuthService(IAuthService):
    def __init__(self, user_repo: IUserRepository, session_file: str = "session.pkl"):
        self.user_repo = user_repo
        self.session_file = session_file
        self._current_user: Optional[User] = None

        self._auto_login()
    
    @property
    def current_user(self) -> Optional[User]:
        return self._current_user
    
    def is_authorized(self) -> bool:
        return self._current_user is not None

    def sign_in(self, login: str, password: str) -> None:
        user = self.user_repo.get_by_login(login)
        if user and user.password == password:
            self._current_user = user
            self._save_session()
            print(f"User {user.name} signed in succesfully.")
        else:
            print("Authorization: wrong login or password.")
    
    def sign_out(self):
        if self._current_user:
            print(f"User {self._current_user.name} had signed out.")
            self._current_user = None
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            return
        else:
            print("Error: no user is signed in.")

    def _save_session(self):
        if self._current_user:
            with open(self.session_file, 'wb') as f:
                pickle.dump(self._current_user.id, f)
    
    def _auto_login(self):
        if not os.path.exists(self.session_file):
            return
        
        try:
            with open(self.session_file, 'rb') as f:
                current_user_id = pickle.load(f)
                user = self.user_repo.get_by_id(current_user_id)
                if  user:
                    self._current_user = user
                    print(f"[Auto-Login] Welcome {self.current_user.name}")
        except Exception as e:
            print(f"Authorization Error: {e}")


def run_demo():
    # Удалим старые файлы БД для чистоты эксперимента
    if os.path.exists("users.db"): os.remove("users.db")
    if os.path.exists("session.pkl"): os.remove("session.pkl")

    print("--- 1. Создание репозитория и добавление пользователей ---")
    repo = FileUserRepository("users.db")
    
    u1 = User(id=1, name="Иван Иванов", login="ivan", password="123", email="ivan@mail.ru")
    u2 = User(id=2, name="Алексей Петров", login="alex", password="321", address="Москва")
    u3 = User(id=3, name="Борис Сидоров", login="boris", password="qwerty")

    repo.add(u1)
    repo.add(u2)
    repo.add(u3)

    print("Все пользователи:", repo.get_all())

    print("\n--- 2. Сортировка пользователей по имени ---")
    sorted_users = sorted(repo.get_all())
    print(f"Отсортировано: {[u.name for u in sorted_users]}")
    # Проверка, что пароль не отображается
    print(f"Строковое представление пользователя (без пароля): {u1}")

    print("\n--- 3. Авторизация ---")
    auth_service = FileAuthService(repo)
    print(f"Авторизован ли кто-то? {auth_service.is_authorized}")
    
    # Попытка войти с неправильным паролем
    auth_service.sign_in("ivan", "wrong_pass")
    
    # Успешный вход
    auth_service.sign_in("ivan", "123")
    print(f"Текущий пользователь: {auth_service.current_user.name}")

    print("\n--- 4. Редактирование пользователя ---")
    # Иван меняет email
    u1_updated = repo.get_by_id(1)
    u1_updated.email = "new_ivan@mail.ru"
    repo.update(u1_updated)
    
    # Проверяем, сохранилось ли в репозитории
    check_user = repo.get_by_id(1)
    print(f"Обновленный email Ивана: {check_user.email}")

    print("\n--- 5. Смена пользователя ---")
    auth_service.sign_out()
    auth_service.sign_in("alex", "321")

    print("\n--- 6. Симуляция перезапуска программы (Авто-авторизация) ---")
    # Удаляем объект сервиса и создаем заново, как будто программа перезапущена
    del auth_service
    
    print("...Программа перезапускается...")
    new_auth_service = FileAuthService(repo) # В конструкторе сработает _auto_login
    
    if new_auth_service.is_authorized:
        print(f"После перезапуска мы авторизованы как: {new_auth_service.current_user.name}")
    else:
        print("Авто-авторизация не сработала.")

run_demo()



