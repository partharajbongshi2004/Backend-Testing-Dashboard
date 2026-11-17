import re
from typing import Dict, List, Union


class StoreValidationError(ValueError):
    """Custom exception for invalid business inputs in the clothing store."""


VALID_ROLES = {"admin", "manager", "cashier", "customer"}
DISCOUNT_TIERS = {
    "NONE": 0.0,
    "WELCOME10": 0.10,
    "VIP20": 0.20,
    "SEASONAL30": 0.30,
}


def calculate_discount(price: float, discount_code: str = "NONE") -> float:
    """
    Calculate the final item price after applying a valid promo code.
    Raises StoreValidationError on negative price or unknown discount code.
    """
    if not isinstance(price, (int, float)) or isinstance(price, bool):
        raise StoreValidationError("Price must be a numeric value.")
    if price < 0:
        raise StoreValidationError("Price cannot be negative.")

    if not isinstance(discount_code, str) or not discount_code.strip():
        raise StoreValidationError("Discount code must be a non-empty string.")

    normalized_code = discount_code.strip().upper()
    if normalized_code not in DISCOUNT_TIERS:
        raise StoreValidationError(f"Invalid discount code: '{discount_code}'.")

    discount_rate = DISCOUNT_TIERS[normalized_code]
    discounted_price = price * (1.0 - discount_rate)
    return round(discounted_price, 2)


def check_inventory_status(
    sku: str,
    current_stock: int,
    reorder_threshold: int = 5,
) -> Dict[str, Union[str, int, bool]]:
    """
    Evaluate stock health for a clothing SKU.
    Returns status ('OUT_OF_STOCK', 'LOW_STOCK', or 'IN_STOCK') and reorder flag.
    """
    if not isinstance(sku, str) or not sku.strip():
        raise StoreValidationError("SKU must be a non-empty string.")
    if not isinstance(current_stock, int) or isinstance(current_stock, bool) or current_stock < 0:
        raise StoreValidationError("Current stock must be a non-negative integer.")
    if not isinstance(reorder_threshold, int) or isinstance(reorder_threshold, bool) or reorder_threshold < 0:
        raise StoreValidationError("Reorder threshold must be a non-negative integer.")

    clean_sku = sku.strip().upper()

    if current_stock == 0:
        status = "OUT_OF_STOCK"
        needs_reorder = True
    elif current_stock <= reorder_threshold:
        status = "LOW_STOCK"
        needs_reorder = True
    else:
        status = "IN_STOCK"
        needs_reorder = False

    return {
        "sku": clean_sku,
        "current_stock": current_stock,
        "status": status,
        "needs_reorder": needs_reorder,
    }


def validate_user_credentials(
    email: str,
    password: str,
    role: str = "customer",
) -> Dict[str, Union[bool, str]]:
    """
    Validate user email format, password complexity, and system role.
    Password rules: >= 8 chars, at least 1 uppercase letter, and at least 1 digit.
    """
    if not isinstance(email, str) or not isinstance(password, str) or not isinstance(role, str):
        raise StoreValidationError("Email, password, and role must be strings.")

    clean_email = email.strip().lower()
    email_pattern = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
    if not re.match(email_pattern, clean_email):
        raise StoreValidationError("Invalid email address format.")

    if len(password) < 8:
        raise StoreValidationError("Password must be at least 8 characters long.")
    if not any(ch.isupper() for ch in password):
        raise StoreValidationError("Password must contain at least one uppercase letter.")
    if not any(ch.isdigit() for ch in password):
        raise StoreValidationError("Password must contain at least one numeric digit.")

    clean_role = role.strip().lower()
    if clean_role not in VALID_ROLES:
        raise StoreValidationError(f"Unsupported user role: '{role}'.")

    return {
        "authenticated": True,
        "email": clean_email,
        "role": clean_role,
    }


def calculate_order_total(
    items: List[Dict[str, Union[str, int, float]]],
    tax_rate: float = 0.08,
    discount_code: str = "NONE",
) -> Dict[str, float]:
    """
    Compute subtotal, promo discount, tax, and grand total for a clothing cart.
    Each item requires 'name', 'unit_price', and 'quantity'.
    """
    if not isinstance(items, list) or len(items) == 0:
        raise StoreValidationError("Order items list cannot be empty.")
    if not isinstance(tax_rate, (int, float)) or isinstance(tax_rate, bool) or not (0.0 <= tax_rate <= 0.5):
        raise StoreValidationError("Tax rate must be between 0.0 and 0.50.")

    raw_subtotal = 0.0
    for item in items:
        if not isinstance(item, dict):
            raise StoreValidationError("Each cart item must be a dictionary.")
        if "unit_price" not in item or "quantity" not in item:
            raise StoreValidationError("Cart items must contain 'unit_price' and 'quantity'.")

        unit_price = item["unit_price"]
        quantity = item["quantity"]

        if not isinstance(unit_price, (int, float)) or isinstance(unit_price, bool) or unit_price < 0:
            raise StoreValidationError("Item unit_price must be a non-negative number.")
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise StoreValidationError("Item quantity must be a positive integer.")

        raw_subtotal += unit_price * quantity

    raw_subtotal = round(raw_subtotal, 2)
    discounted_subtotal = calculate_discount(raw_subtotal, discount_code)
    discount_amount = round(raw_subtotal - discounted_subtotal, 2)
    tax_amount = round(discounted_subtotal * tax_rate, 2)
    grand_total = round(discounted_subtotal + tax_amount, 2)

    return {
        "subtotal": raw_subtotal,
        "discount_amount": discount_amount,
        "tax_amount": tax_amount,
        "grand_total": grand_total,
    }
