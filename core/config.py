from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración general de la aplicación cargada desde variables de entorno."""

    APP_NAME: str = "Sistema de Inventario de Equipos Informaticos"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Base de datos MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "inventario_equipos_db"
    MONGODB_DATABASE: str = ""
    MONGODB_COLLECTION: str = "equipos"

    def model_post_init(self, __context):
        if self.MONGODB_DATABASE and (not self.MONGODB_DB or self.MONGODB_DB == "inventario_equipos_db"):
            self.MONGODB_DB = self.MONGODB_DATABASE

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia singleton en caché de la configuración."""
    return Settings()


settings = get_settings()
