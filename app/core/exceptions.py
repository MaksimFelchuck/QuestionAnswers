class UserNotFoundError(Exception):
    """Пользователь не найден"""
    pass


class AuthenticationError(Exception):
    """Ошибка аутентификации"""
    pass


class InvalidTokenError(Exception):
    """Недействительный токен"""
    pass


class UserAlreadyExistsError(Exception):
    """Пользователь уже существует"""
    pass
