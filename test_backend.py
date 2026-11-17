import pytest
from backend_app import (
    StoreValidationError,
    calculate_discount,
    calculate_order_total,
    check_inventory_status,
    validate_user_credentials,
)


# ==========================================
# 1. UNIT TESTS: DISCOUNT CALCULATION
# ==========================================
class TestDiscountCalculation:
    @pytest.mark.parametrize(
        "price,code,expected",
        [
            (100.0, "NONE", 100.0),
            (100.0, "WELCOME10", 90.0),
            (85.50, "vip20", 68.40),
            (200.0, " SEASONAL30 ", 140.0),
            (0.0, "VIP20", 0.0),
        ],
    )
    def test_valid_discounts(self, price, code, expected):
        assert calculate_discount(price, code) == expected

    def test_negative_price_raises_error(self):
        with pytest.raises(StoreValidationError, match="Price cannot be negative"):
            calculate_discount(-25.0, "WELCOME10")

    def test_non_numeric_price_raises_error(self):
        with pytest.raises(StoreValidationError, match="Price must be a numeric value"):
            calculate_discount("100", "WELCOME10")

    def test_invalid_promo_code_raises_error(self):
        with pytest.raises(StoreValidationError, match="Invalid discount code"):
            calculate_discount(50.0, "FAKE50")

    def test_empty_promo_code_raises_error(self):
        with pytest.raises(StoreValidationError, match="non-empty string"):
            calculate_discount(50.0, "   ")


# ==========================================
# 2. UNIT TESTS: INVENTORY STOCK CHECKER
# ==========================================
class TestInventoryStatus:
    def test_in_stock_status(self):
        result = check_inventory_status("ts-blk-m", current_stock=25, reorder_threshold=5)
        assert result == {
            "sku": "TS-BLK-M",
            "current_stock": 25,
            "status": "IN_STOCK",
            "needs_reorder": False,
        }

    def test_low_stock_boundary_status(self):
        result = check_inventory_status("hd-gry-l", current_stock=5, reorder_threshold=5)
        assert result["status"] == "LOW_STOCK"
        assert result["needs_reorder"] is True

    def test_out_of_stock_status(self):
        result = check_inventory_status("jn-blu-32", current_stock=0, reorder_threshold=5)
        assert result["status"] == "OUT_OF_STOCK"
        assert result["needs_reorder"] is True

    def test_negative_stock_raises_error(self):
        with pytest.raises(StoreValidationError, match="non-negative integer"):
            check_inventory_status("TS-BLK-M", current_stock=-1)

    def test_blank_sku_raises_error(self):
        with pytest.raises(StoreValidationError, match="SKU must be a non-empty string"):
            check_inventory_status("   ", current_stock=10)


# ==========================================
# 3. UNIT TESTS: USER AUTHENTICATION
# ==========================================
class TestUserCredentials:
    def test_valid_user_credentials(self):
        res = validate_user_credentials("Manager@UrbanThreads.com", "SecurePass9", "Manager")
        assert res == {
            "authenticated": True,
            "email": "manager@urbanthreads.com",
            "role": "manager",
        }

    @pytest.mark.parametrize(
        "bad_email",
        ["plainaddress", "missing@domain", "@nouser.com", "user@.com"],
    )
    def test_invalid_email_formats(self, bad_email):
        with pytest.raises(StoreValidationError, match="Invalid email address format"):
            validate_user_credentials(bad_email, "StrongPass1", "customer")

    def test_short_password_rejected(self):
        with pytest.raises(StoreValidationError, match="at least 8 characters"):
            validate_user_credentials("user@store.com", "Ab12345", "customer")

    def test_password_missing_uppercase_rejected(self):
        with pytest.raises(StoreValidationError, match="one uppercase letter"):
            validate_user_credentials("user@store.com", "lowercase123", "customer")

    def test_password_missing_digit_rejected(self):
        with pytest.raises(StoreValidationError, match="one numeric digit"):
            validate_user_credentials("user@store.com", "NoNumbersHere", "customer")

    def test_invalid_role_rejected(self):
        with pytest.raises(StoreValidationError, match="Unsupported user role"):
            validate_user_credentials("user@store.com", "ValidPass1", "superhacker")


# ==========================================
# 4. INTEGRATION TESTS: ORDER TOTAL & TAX
# ==========================================
class TestOrderTotalIntegration:
    def test_complete_order_with_discount_and_tax(self):
        cart = [
            {"name": "Cotton T-Shirt", "unit_price": 25.00, "quantity": 2},
            {"name": "Denim Jacket", "unit_price": 100.00, "quantity": 1},
        ]
        # Raw subtotal = 150.00
        # VIP20 (20% off) = 120.00 (Discount = 30.00)
        # 10% tax on 120.00 = 12.00
        # Grand total = 132.00
        summary = calculate_order_total(cart, tax_rate=0.10, discount_code="VIP20")
        assert summary == {
            "subtotal": 150.00,
            "discount_amount": 30.00,
            "tax_amount": 12.00,
            "grand_total": 132.00,
        }

    def test_empty_cart_raises_error(self):
        with pytest.raises(StoreValidationError, match="cannot be empty"):
            calculate_order_total([])

    def test_invalid_tax_rate_raises_error(self):
        cart = [{"name": "Socks", "unit_price": 10.00, "quantity": 1}]
        with pytest.raises(StoreValidationError, match="Tax rate must be between"):
            calculate_order_total(cart, tax_rate=0.75)

    def test_zero_quantity_item_raises_error(self):
        cart = [{"name": "Socks", "unit_price": 10.00, "quantity": 0}]
        with pytest.raises(StoreValidationError, match="positive integer"):
            calculate_order_total(cart)
