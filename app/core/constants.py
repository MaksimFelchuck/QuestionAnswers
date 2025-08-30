# HTTP статусы
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_500_INTERNAL_SERVER_ERROR = 500

# Сообщения об ошибках
USER_NOT_FOUND = "User not found"
USER_ALREADY_EXISTS = "User already exists"
AUTHENTICATION_FAILED = "Authentication failed"
INVALID_TOKEN = "Invalid token"
INVALID_REFRESH_TOKEN = "Invalid refresh token"
DATA_INTEGRITY_VIOLATION = "Data integrity violation"
VALIDATION_ERROR = "Validation error"
INTERNAL_SERVER_ERROR = "Internal server error"

# Сообщения об успехе
USER_SUCCESSFULLY_DELETED = "Пользователь успешно удален"
SUCCESSFUL_LOGOUT = "Успешный выход"

# JWT токены
TOKEN_TYPE_BEARER = "bearer"
TOKEN_TYPE_REFRESH = "refresh"

# Поля токенов
TOKEN_SUBJECT = "sub"
TOKEN_USER_ID = "user_id"
TOKEN_TYPE = "type"
