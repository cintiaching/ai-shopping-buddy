from dotenv import load_dotenv

from chatbots.utils.logger import _configure_loggers

load_dotenv()
_configure_loggers(__name__)
