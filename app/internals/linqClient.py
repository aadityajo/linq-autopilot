from linq import LinqAPIV3
from app.config import settings

client = LinqAPIV3(api_key=settings.linq_api_key)
