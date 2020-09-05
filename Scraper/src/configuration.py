from dataclasses import dataclass

# https://tech.preferred.jp/en/blog/working-with-configuration-in-python/

@dataclass
class MongoConfiguration:
    collection: str
    database: str
    user: str
    pw: str
    url: str


@dataclass
class BackendConfiguration:
    SCHEDULER_API_ENABLED: bool = True


@dataclass
class Configuration:
    backend: BackendConfiguration
    database: MongoConfiguration
