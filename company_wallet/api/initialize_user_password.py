from .utils import unify_response
from company_wallet.company_wallet.doctype.wallet_user.wallet_user import initialize_password


@unify_response()
def initialize_user_password(user):
    """
    Initializes the password for a given user.
    Args:
    user (str): The username of the user.
    Returns:
    None
    """
    initialize_password(user)
