import enum

# ================== ENUMS ==================
class DeviceType(enum.Enum):
    mobile = "Mobile"
    tablet = "Tablet"
    desktop = "Desktop"
    smart_tv = "Smart TV"
    gaming = "Gaming Console"
    iot = "IoT Device"
    unknown = "Unknown"


class SessionStatus(enum.Enum):
    active = "Active"
    expired = "Expired"
    revoked = "Revoked"
    logged_out = "Logged Out"
    suspicious = "Suspicious"


class AuthMethod(enum.Enum):
    password = "Password"
    otp = "One-Time Password"
    biometric = "Biometric"
    security_key = "Security Key"
    social = "Social Login"


class NotificationType(enum.Enum):
    push = "Push Notification"
    email = "Email"
    sms = "SMS"
    in_app = "In-App"


class UserRole(enum.Enum):
    SUPER_ADMIN = "SuperAdmin"
    USER = "User"
    ADMIN = "Admin"
    SUPERUSER = "Superuser"

class SocialProvider(enum.Enum):
    google = "Google"
    icloud = "iCloud"