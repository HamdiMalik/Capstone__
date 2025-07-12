from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .scan import Scan
from .notification import Notification
from .device_info import DeviceInfo