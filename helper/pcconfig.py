import pynecone as pc

class HelperConfig(pc.Config):
    pass

config = HelperConfig(
    app_name="helper",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)