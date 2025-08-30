from dependency_injector import containers, providers
from app.core.database import SessionLocal, engine
from app.repositories.user.in_mem import InMemUserRepository
from app.repositories.user.db import DBUserRepository


class Container(containers.DeclarativeContainer):
    # Конфигурация
    config = providers.Configuration()
    
    # База данных
    db_session = providers.Singleton(SessionLocal)
    db_engine = providers.Singleton(engine)
    
    # Репозитории
    user_repository = providers.Selector(
        config.test_mode,
        test=providers.Factory(InMemUserRepository),
        prod=providers.Factory(DBUserRepository, db=db_session),
        default=providers.Factory(DBUserRepository, db=db_session)
    )
    
