class AuthenticationError(Exception):
    """Raised when there is an issue with authentication details, username or password"""


class InvoiceVerificationError(Exception):
    """Raised when there is an issue with verifying an invoice posted to OBR"""


class InvoiceAdditionError(Exception):
    """Raised when there is an issue with adding an invoice to the eBMS database."""


class TINVerificationError(Exception):
    """Raised when there is an issue with verifying a TIN no of the business."""


class InvoiceCancellationError(Exception):
    """Raised when there is an issue with canceling an invoice that was already added to eBIMS database."""


class StockMovementError(Exception):
    """Raised when there is an issue with adding stock movements during OBR integration."""


class InvalidURLException(Exception):
    """Raised when an invalid URL is provided in prod/testing APIs"""


class TokenExpiredError(Exception):
    """Raised when the authentication token has expired."""


