
from environs import Env

def get_progress_bar_disabled() -> bool:
    env = Env()
    env.read_env()
    enabled: bool = env.bool("PROGRESS_BAR_FLAG", True)
    return not enabled
