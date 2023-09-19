import pynecone as pc

class KakaosinkConfig(pc.Config):
    pass

config = KakaosinkConfig(
    app_name="kakaosink",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)