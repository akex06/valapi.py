import msgspec

from valorant import Account


class Password(msgspec.Struct):
    change_at: int = msgspec.field(name="cng_at")
    reset: bool
    must_reset: bool


class User(
    msgspec.Struct,
    rename={
        "player_id": "sub",
        "is_email_verified": "email_verified",
        "password": "pw",
        "is_phone_number_verified": "phone_number_verified",
        "account": "acct",
    },
):
    country: str
    player_id: str
    is_email_verified: bool
    password: Password
    is_phone_number_verified: bool
    account: Account
    jti: str
    country_at: int | None = None
    ppid: str | None = None
    player_locale: str | None = None
