from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    host: str = Field(default='0.0.0.0', alias='HOST')
    port: int = Field(default=5000, alias='PORT')
    log_level: str = Field(default='info', alias='LOG_LEVEL')

    ollama_base_url: str = Field(default='http://localhost:11434', alias='OLLAMA_BASE_URL')
    ollama_model: str = Field(default='phi3:mini', alias='OLLAMA_MODEL')

    google_api_key: str | None = Field(default=None, alias='GOOGLE_API_KEY')
    gemini_model: str = Field(default='gemini-1.5-flash', alias='GEMINI_MODEL')

    hard_query_word_threshold: int = Field(default=20, alias='HARD_QUERY_WORD_THRESHOLD')
    enable_web_search: bool = Field(default=True, alias='ENABLE_WEB_SEARCH')
    search_results_limit: int = Field(default=3, alias='SEARCH_RESULTS_LIMIT')

    openclaw_base_url: str | None = Field(default=None, alias='OPENCLAW_BASE_URL')


settings = Settings()
