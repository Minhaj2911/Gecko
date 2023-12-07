from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Generates a unique token for account activation. Inherits from Django's PasswordResetTokenGenerator.
    The token combines the user's ID, a timestamp, and their active status to ensure uniqueness and security."""
    
    def _make_hash_value(self, user, timestamp):
        """
        Creates a hash value for the token.

        Parameters:
        - user (User): User instance for whom the token is generated.
        - timestamp (int): Time of token generation.

        Returns:
        - str: Hash value for the token.
        """
        return (text_type(user.pk) + text_type(timestamp) + text_type(user.is_active))

account_activation_token = AccountActivationTokenGenerator()
