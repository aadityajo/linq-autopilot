from linq import LinqAPIV3
import os

client = LinqAPIV3(api_key=os.environ.get("LINQ_API_KEY"))
