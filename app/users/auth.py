
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy import JWTStrategy
from fastapi_users import FastAPIUsers

from users.manager import get_user_manager
from config import settings
from users.models import User

SECRET = settings.JWT_SECRET

# в качестве транспорта используется Bearer
bearer_transport = BearerTransport(tokenUrl="users/auth/jwt/login")


# в качестве механизма аутентификации - JWT
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# указываем классу FastAPIUsers желаемую модель юзера и тип идентификатора
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)

current_user = fastapi_users.current_user()

