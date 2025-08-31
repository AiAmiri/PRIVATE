from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import (
    Currency,
    SupportedCurrency,
    SarafProfile,
    sendhawala,
)


class CoreModelsTestCase(TestCase):
    def test_only_one_default_currency(self):
        """
        Saving a currency with is_default=True should unset is_default on any existing default currency.
        """
        usd = Currency.objects.create(code="USD", name="US Dollar", symbol="$", is_active=True, is_default=True,
                                      exchange_rate=Decimal("1.000000"))
        eur = Currency.objects.create(code="EUR", name="Euro", symbol="€", is_active=True, is_default=True,
                                      exchange_rate=Decimal("1.100000"))

        # Refresh from DB to capture updates from save()
        usd.refresh_from_db()
        eur.refresh_from_db()

        self.assertFalse(usd.is_default, "Previous default currency should be unset")
        self.assertTrue(eur.is_default, "Newly saved default currency should remain default")
        self.assertEqual(Currency.get_default_currency(), eur)

    def test_supported_currency_effective_rate_uses_custom_then_falls_back(self):
        """
        SupportedCurrency.get_effective_rate should use custom_rate when present, otherwise the currency's exchange_rate.
        """
        base = Currency.objects.create(code="USD", name="US Dollar", symbol="$", is_active=True, is_default=True,
                                       exchange_rate=Decimal("1.000000"))
        eur = Currency.objects.create(code="EUR", name="Euro", symbol="€", is_active=True, is_default=False,
                                      exchange_rate=Decimal("1.250000"))
        saraf = SarafProfile.objects.create(
            name="Ali",
            last_name="Khan",
            phone="+10000000001",
            email="ali@example.com",
            password_hash="init",
            license_no="LIC-001",
            saraf_address="Some Address",
            about_us="About",
            work_history=5,
        )

        sc_custom = SupportedCurrency.objects.create(saraf=saraf, currency=eur, custom_rate=Decimal("1.230000"))
        self.assertEqual(sc_custom.get_effective_rate(), Decimal("1.230000"))

        sc_default = SupportedCurrency.objects.create(saraf=saraf, currency=base)
        self.assertEqual(sc_default.get_effective_rate(), Decimal("1.000000"))

    def test_sendhawala_amount_conversion_to_default_currency(self):
        """
        sendhawala.get_amount_in_default_currency should convert using the transaction currency's exchange_rate.
        """
        usd = Currency.objects.create(code="USD", name="US Dollar", symbol="$", is_active=True, is_default=True,
                                      exchange_rate=Decimal("1.000000"))
        eur = Currency.objects.create(code="EUR", name="Euro", symbol="€", is_active=True, is_default=False,
                                      exchange_rate=Decimal("1.200000"))

        tx = sendhawala.objects.create(
            hawala_number=1001,
            sender_name="Sender A",
            receiver_name="Receiver B",
            amount=Decimal("100.00"),
            currency=eur,
            rate_type="market",
            receiver_location="Paris",
            exchanger_location="NYC",
            sender_phone="+15550000001",
        )

        self.assertEqual(tx.get_amount_in_default_currency(), Decimal("120.00"))

        # If transaction is already in default currency, amount should be unchanged
        tx2 = sendhawala.objects.create(
            hawala_number=1002,
            sender_name="Sender C",
            receiver_name="Receiver D",
            amount=Decimal("50.00"),
            currency=usd,
            rate_type="market",
            receiver_location="Berlin",
            exchanger_location="LA",
            sender_phone="+15550000002",
        )
        self.assertEqual(tx2.get_amount_in_default_currency(), Decimal("50.00"))

    def test_saraf_password_validation_and_hashing(self):
        """
        SarafProfile.set_password should reject weak passwords and persist a hashed password for strong ones.
        """
        saraf = SarafProfile.objects.create(
            name="Sara",
            last_name="Lee",
            phone="+10000000002",
            email="sara@example.com",
            password_hash="init",
            license_no="LIC-002",
            saraf_address="Some Address",
            about_us="About",
            work_history=3,
        )

        # Weak password should raise ValidationError (fails multiple strength checks)
        with self.assertRaises(ValidationError):
            saraf.set_password("short")  # too short and lacks complexity

        strong_pwd = "Strong1!"
        saraf.set_password(strong_pwd)
        self.assertNotEqual(saraf.password_hash, strong_pwd)
        self.assertTrue(saraf.check_password(strong_pwd))

    def test_get_supported_currencies_returns_only_active(self):
        """
        SarafProfile.get_supported_currencies should include only SupportedCurrency with is_active=True.
        """
        Currency.objects.create(code="USD", name="US Dollar", symbol="$", is_active=True, is_default=True,
                                exchange_rate=Decimal("1.000000"))
        eur = Currency.objects.create(code="EUR", name="Euro", symbol="€", is_active=True, is_default=False,
                                      exchange_rate=Decimal("1.100000"))
        gbp = Currency.objects.create(code="GBP", name="Pound Sterling", symbol="£", is_active=True, is_default=False,
                                      exchange_rate=Decimal("1.300000"))
        saraf = SarafProfile.objects.create(
            name="Noor",
            last_name="Khan",
            phone="+10000000003",
            email="noor@example.com",
            password_hash="init",
            license_no="LIC-003",
            saraf_address="Some Address",
            about_us="About",
            work_history=7,
        )

        SupportedCurrency.objects.create(saraf=saraf, currency=eur, is_active=True)
        SupportedCurrency.objects.create(saraf=saraf, currency=gbp, is_active=False)

        supported = saraf.get_supported_currencies()
        self.assertQuerysetEqual(
            supported.order_by("code").values_list("code", flat=True),
            ["EUR"],
            transform=list,
        )
