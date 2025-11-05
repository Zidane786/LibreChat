"""Two-Factor Authentication (TOTP) utilities"""
import pyotp
import qrcode
import io
import base64
from typing import Tuple, List
from app.utils.auth import hash_password


def generate_totp_secret() -> str:
    """
    Generate a new TOTP secret

    Returns:
        Base32 encoded secret
    """
    return pyotp.random_base32()


def generate_totp_qr_code(secret: str, email: str, issuer: str = "LibreChat") -> str:
    """
    Generate QR code for TOTP setup

    Args:
        secret: TOTP secret
        email: User email
        issuer: Issuer name

    Returns:
        Base64 encoded QR code image
    """
    # Create provisioning URI
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=email,
        issuer_name=issuer
    )

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def verify_totp_code(secret: str, code: str) -> bool:
    """
    Verify TOTP code

    Args:
        secret: TOTP secret
        code: User provided code

    Returns:
        True if code is valid, False otherwise
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # Allow 1 time step tolerance


def generate_backup_codes(count: int = 10) -> Tuple[List[str], List[dict]]:
    """
    Generate backup codes for 2FA

    Args:
        count: Number of backup codes to generate

    Returns:
        Tuple of (plain codes, hashed code objects)
    """
    codes = []
    hashed_codes = []

    for _ in range(count):
        # Generate 8-character alphanumeric code
        code = pyotp.random_base32(length=8)
        codes.append(code)

        # Hash the code for storage
        hashed_codes.append({
            "code_hash": hash_password(code),
            "used": False,
            "used_at": None
        })

    return codes, hashed_codes
