from sqlalchemy import Column, String, Enum, Boolean, ForeignKey, DateTime, Index, Text, JSON, Integer, text
from sqlalchemy.dialects.postgresql import UUID, INET, MACADDR, ARRAY
from sqlalchemy.orm import relationship

from app.models import Base, IntIdMixin, TimeStampMixin
from app.models.enums import DeviceType, SessionStatus, AuthMethod, NotificationType


# ================== MODELS ==================
class UserDevice(Base, IntIdMixin, TimeStampMixin):
    __tablename__ = "user_device"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_name = Column(String(100), nullable=True)
    device_type = Column(Enum(DeviceType), default=DeviceType.unknown, nullable=False)
    device_model = Column(String(100), nullable=True)
    device_manufacturer = Column(String(100), nullable=True)

    # OS Information
    os_name = Column(String(50), nullable=True)
    os_version = Column(String(50), nullable=True)

    # Browser Information
    browser_name = Column(String(50), nullable=True)
    browser_version = Column(String(50), nullable=True)

    # Network Information
    last_ip_address = Column(INET, nullable=True)
    last_mac_address = Column(MACADDR, nullable=True)
    vpn_used = Column(Boolean, default=False, nullable=False)

    # Device Identification
    device_identifier = Column(String(255), unique=True, nullable=True)
    fingerprint = Column(JSON, nullable=True)  # Device fingerprint JSON

    # Security Flags
    is_trusted = Column(Boolean, default=False, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    risk_score = Column(Integer, default=0, nullable=False)

    # Push Notifications
    push_token = Column(String(255), nullable=True)
    notification_preferences = Column(ARRAY(Enum(NotificationType)),
                                      default=[NotificationType.push],
                                      nullable=False)

    # 2FA Methods
    supported_auth_methods = Column(ARRAY(Enum(AuthMethod)), nullable=False)

    # Location
    last_known_latitude = Column(String(20), nullable=True)
    last_known_longitude = Column(String(20), nullable=True)
    last_known_location = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="devices")
    sessions = relationship("UserSession", back_populates="device", cascade="all, delete-orphan")
    authenticators = relationship("DeviceAuthenticator", back_populates="device", cascade="all, delete-orphan")


class UserSession(Base, IntIdMixin, TimeStampMixin):
    __tablename__ = "user_session"
    __table_args__ = (
        Index('ix_user_session_composite', 'user_id', 'status', 'expires_at'),
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("user_device.id"), nullable=True)

    # Authentication Info
    session_token = Column(String(512), nullable=False, unique=True)
    refresh_token = Column(String(512), nullable=True, unique=True)
    auth_method = Column(Enum(AuthMethod), nullable=False)
    mfa_used = Column(Boolean, default=False, nullable=False)

    # Client Info
    ip_address = Column(INET, nullable=False)
    user_agent = Column(Text, nullable=True)
    client_info = Column(JSON, nullable=True)  # Parsed user_management agent data

    # Status & Timing
    status = Column(Enum(SessionStatus), default=SessionStatus.active, nullable=False)
    login_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    # Location Data
    login_location = Column(String(255), nullable=True)
    login_latitude = Column(String(20), nullable=True)
    login_longitude = Column(String(20), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    device = relationship("UserDevice", back_populates="sessions")
    activities = relationship("SessionActivity", back_populates="session", cascade="all, delete-orphan")


class DeviceAuthenticator(Base, IntIdMixin, TimeStampMixin):
    __tablename__ = "device_authenticator"

    device_id = Column(Integer, ForeignKey("user_device.id"), nullable=False)
    auth_method = Column(Enum(AuthMethod), nullable=False)
    public_key = Column(Text, nullable=True)  # For security keys
    secret = Column(String(255), nullable=True)  # For OTP secrets
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    device = relationship("UserDevice", back_populates="authenticators")


class SessionActivity(Base, IntIdMixin, TimeStampMixin):
    __tablename__ = "session_activity"
    __table_args__ = (
        Index('ix_session_activity_session', 'session_id', 'activity_type'),
    )

    session_id = Column(Integer, ForeignKey("user_session.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)

    # Rename this column to avoid conflict with SQLAlchemy's metadata
    activity_metadata = Column(JSON, nullable=True, name="metadata")

    # Relationships
    session = relationship("UserSession", back_populates="activities")
