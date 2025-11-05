import secrets
import string
import time
from datetime import datetime, timezone, timedelta
from enum import Enum


class IDPrefix(Enum):
    """Prefixes for different ID types"""
    SUPERUSER = "SU"
    SUPER_ADMIN = "SA"
    ADMIN = "AD"


class GeneratorManager:
    # Base62 character set (0-9, A-Z, a-z)
    Base62 = string.digits + string.ascii_letters

    @classmethod
    def base62_encode(cls, number: int) -> str:
        """Encode number to base62 string"""
        if number == 0:
            return cls.Base62[0]
        encoded = []
        while number > 0:
            number, remainder = divmod(number, 62)
            encoded.append(cls.Base62[remainder])
        return "".join(reversed(encoded))

    @classmethod
    def generate_timestamp_component(cls) -> str:
        """Generate timestamp component (millisecond precision)"""
        return cls.base62_encode(int(time.time() * 1000))

    @classmethod
    def generate_random_component(cls, length: int) -> str:
        """Generate cryptographically secure random component"""
        return "".join(secrets.choice(cls.Base62) for _ in range(length))

    @classmethod
    def generate_id(cls, prefix: IDPrefix, total_length: int = 12) -> str:
        """
        Generate a unique ID with:
        - Prefix (2 chars)
        - Timestamp (variable)
        - Random component (remaining)
        """
        if total_length < 8:
            raise ValueError("ID length must be at least 8 characters")

        prefix_part = prefix.value
        timestamp_part = cls.generate_timestamp_component()
        remaining_length = total_length - len(prefix_part)

        # Ensure minimum randomness
        min_random = 4
        if len(timestamp_part) > remaining_length - min_random:
            timestamp_part = timestamp_part[:remaining_length - min_random]

        random_part = cls.generate_random_component(remaining_length - len(timestamp_part))
        return f"{prefix_part}{timestamp_part}{random_part}"

    @staticmethod
    def generate_digits_code(code_length: int) -> str:
        """Generate a numeric code of given length"""
        return "".join(secrets.choice(string.digits) for _ in range(code_length))

    @staticmethod
    def expires_at(expire_minutes: int):
        """Generate an expiry datetime"""
        return datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
