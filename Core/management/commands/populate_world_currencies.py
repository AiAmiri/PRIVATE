from django.core.management.base import BaseCommand
from Core.models import Currency
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with worldwide currencies'

    def handle(self, *args, **options):
        # Comprehensive list of world currencies with ISO 4217 codes, English names, and Farsi names
        # Format: (code, name, symbol, rate, english_name, farsi_name)
        world_currencies = [
            # Major currencies
            ('USD', 'US Dollar', '$', 1.0, 'US Dollar', 'دالر آمریکا'),
            ('EUR', 'Euro', '€', 0.85, 'Euro', 'یورو'),
            ('GBP', 'British Pound', '£', 0.75, 'British Pound', 'پوند انگلیس'),
            ('JPY', 'Japanese Yen', '¥', 110.0, 'Japanese Yen', 'ین ژاپن'),
            ('CHF', 'Swiss Franc', 'CHF', 0.92, 'Swiss Franc', 'فرانک سوئیس'),
            ('CAD', 'Canadian Dollar', 'C$', 1.25, 'Canadian Dollar', 'دالر کانادا'),
            ('AUD', 'Australian Dollar', 'A$', 1.35, 'Australian Dollar', 'دالر استرالیا'),
            ('NZD', 'New Zealand Dollar', 'NZ$', 1.45, 'New Zealand Dollar', 'دالر نیوزیلند'),
            
            # Middle East & South Asia
            ('AFN', 'Afghan Afghani', '؋', 88.5, 'Afghan Afghani', 'افغانی افغانستان'),
            ('PKR', 'Pakistani Rupee', '₨', 280.0, 'Pakistani Rupee', 'روپیه پاکستان'),
            ('INR', 'Indian Rupee', '₹', 83.0, 'Indian Rupee', 'روپیه هند'),
            ('IRR', 'Iranian Rial', '﷼', 42000.0, 'Iranian Rial', 'ریال ایران'),
            ('AED', 'UAE Dirham', 'د.إ', 3.673, 'UAE Dirham', 'درهم امارات'),
            ('SAR', 'Saudi Riyal', '﷼', 3.75, 'Saudi Riyal', 'ریال عربستان'),
            ('QAR', 'Qatari Riyal', 'ر.ق', 3.64, 'Qatari Riyal', 'ریال قطر'),
            ('KWD', 'Kuwaiti Dinar', 'د.ك', 0.307, 'Kuwaiti Dinar', 'دینار کویت'),
            ('BHD', 'Bahraini Dinar', '.د.ب', 0.377, 'Bahraini Dinar', 'دینار بحرین'),
            ('OMR', 'Omani Rial', 'ر.ع.', 0.385, 'Omani Rial', 'ریال عمان'),
            ('JOD', 'Jordanian Dinar', 'د.ا', 0.709, 'Jordanian Dinar', 'دینار اردن'),
            ('LBP', 'Lebanese Pound', 'ل.ل', 15000.0, 'Lebanese Pound', 'لیره لبنان'),
            ('SYP', 'Syrian Pound', '£S', 2512.0, 'Syrian Pound', 'لیره سوریه'),
            ('IQD', 'Iraqi Dinar', 'ع.د', 1310.0, 'Iraqi Dinar', 'دینار عراق'),
            ('YER', 'Yemeni Rial', '﷼', 250.0, 'Yemeni Rial', 'ریال یمن'),
            ('TRY', 'Turkish Lira', '₺', 27.0, 'Turkish Lira', 'لیره ترکیه'),
            ('ILS', 'Israeli New Shekel', '₪', 3.7, 'Israeli New Shekel', 'شکل جدید اسرائیل'),
            
            # East Asia
            ('CNY', 'Chinese Yuan', '¥', 7.2),
            ('KRW', 'South Korean Won', '₩', 1320.0),
            ('HKD', 'Hong Kong Dollar', 'HK$', 7.8),
            ('SGD', 'Singapore Dollar', 'S$', 1.35),
            ('TWD', 'Taiwan Dollar', 'NT$', 31.5),
            ('MYR', 'Malaysian Ringgit', 'RM', 4.65),
            ('THB', 'Thai Baht', '฿', 35.5),
            ('IDR', 'Indonesian Rupiah', 'Rp', 15500.0),
            ('PHP', 'Philippine Peso', '₱', 56.0),
            ('VND', 'Vietnamese Dong', '₫', 24500.0),
            ('LAK', 'Lao Kip', '₭', 20500.0),
            ('KHR', 'Cambodian Riel', '៛', 4100.0),
            ('MMK', 'Myanmar Kyat', 'Ks', 2100.0),
            ('BDT', 'Bangladeshi Taka', '৳', 110.0),
            ('LKR', 'Sri Lankan Rupee', 'Rs', 325.0),
            ('NPR', 'Nepalese Rupee', 'Rs', 133.0),
            ('BTN', 'Bhutanese Ngultrum', 'Nu.', 83.0),
            ('MVR', 'Maldivian Rufiyaa', 'Rf', 15.4),
            
            # Europe
            ('NOK', 'Norwegian Krone', 'kr', 10.8),
            ('SEK', 'Swedish Krona', 'kr', 10.9),
            ('DKK', 'Danish Krone', 'kr', 6.9),
            ('ISK', 'Icelandic Krona', 'kr', 138.0),
            ('PLN', 'Polish Zloty', 'zł', 4.3),
            ('CZK', 'Czech Koruna', 'Kč', 22.5),
            ('HUF', 'Hungarian Forint', 'Ft', 360.0),
            ('RON', 'Romanian Leu', 'lei', 4.95),
            ('BGN', 'Bulgarian Lev', 'лв', 1.8),
            ('HRK', 'Croatian Kuna', 'kn', 7.5),
            ('RSD', 'Serbian Dinar', 'дин', 107.0),
            ('BAM', 'Bosnia-Herzegovina Mark', 'KM', 1.8),
            ('MKD', 'Macedonian Denar', 'ден', 56.0),
            ('ALL', 'Albanian Lek', 'L', 95.0),
            ('RUB', 'Russian Ruble', '₽', 95.0),
            ('UAH', 'Ukrainian Hryvnia', '₴', 37.0),
            ('BYN', 'Belarusian Ruble', 'Br', 2.5),
            ('MDL', 'Moldovan Leu', 'L', 18.0),
            ('GEL', 'Georgian Lari', '₾', 2.65),
            ('AMD', 'Armenian Dram', '֏', 385.0),
            ('AZN', 'Azerbaijani Manat', '₼', 1.7),
            ('KZT', 'Kazakhstani Tenge', '₸', 450.0),
            ('UZS', 'Uzbekistani Som', 'soʻm', 12300.0),
            ('TJS', 'Tajikistani Somoni', 'SM', 10.9),
            ('KGS', 'Kyrgystani Som', 'с', 89.0),
            ('TMT', 'Turkmenistani Manat', 'm', 3.5),
            
            # Africa
            ('ZAR', 'South African Rand', 'R', 18.5),
            ('EGP', 'Egyptian Pound', '£E', 31.0),
            ('NGN', 'Nigerian Naira', '₦', 775.0),
            ('KES', 'Kenyan Shilling', 'Sh', 150.0),
            ('TZS', 'Tanzanian Shilling', 'Sh', 2500.0),
            ('UGX', 'Ugandan Shilling', 'Sh', 3700.0),
            ('RWF', 'Rwandan Franc', 'Fr', 1200.0),
            ('ETB', 'Ethiopian Birr', 'Br', 55.0),
            ('GHS', 'Ghanaian Cedi', '₵', 12.0),
            ('XOF', 'West African CFA Franc', 'Fr', 600.0),
            ('XAF', 'Central African CFA Franc', 'Fr', 600.0),
            ('MAD', 'Moroccan Dirham', 'د.م.', 10.2),
            ('TND', 'Tunisian Dinar', 'د.ت', 3.1),
            ('DZD', 'Algerian Dinar', 'د.ج', 135.0),
            ('LYD', 'Libyan Dinar', 'ل.د', 4.8),
            ('SDG', 'Sudanese Pound', 'ج.س.', 600.0),
            ('SOS', 'Somali Shilling', 'Sh', 570.0),
            ('DJF', 'Djiboutian Franc', 'Fr', 178.0),
            ('ERN', 'Eritrean Nakfa', 'Nfk', 15.0),
            ('MWK', 'Malawian Kwacha', 'MK', 1030.0),
            ('ZMW', 'Zambian Kwacha', 'ZK', 22.0),
            ('BWP', 'Botswanan Pula', 'P', 13.5),
            ('SZL', 'Swazi Lilangeni', 'L', 18.5),
            ('LSL', 'Lesotho Loti', 'L', 18.5),
            ('NAD', 'Namibian Dollar', 'N$', 18.5),
            ('MZN', 'Mozambican Metical', 'MT', 64.0),
            ('AOA', 'Angolan Kwanza', 'Kz', 825.0),
            ('ZWL', 'Zimbabwean Dollar', 'Z$', 322.0),
            ('MUR', 'Mauritian Rupee', '₨', 45.0),
            ('SCR', 'Seychellois Rupee', '₨', 13.5),
            ('KMF', 'Comorian Franc', 'Fr', 450.0),
            ('MGA', 'Malagasy Ariary', 'Ar', 4500.0),
            
            # Americas
            ('MXN', 'Mexican Peso', '$', 17.5),
            ('BRL', 'Brazilian Real', 'R$', 5.0),
            ('ARS', 'Argentine Peso', '$', 350.0),
            ('CLP', 'Chilean Peso', '$', 900.0),
            ('COP', 'Colombian Peso', '$', 4000.0),
            ('PEN', 'Peruvian Sol', 'S/', 3.7),
            ('UYU', 'Uruguayan Peso', '$', 39.0),
            ('PYG', 'Paraguayan Guarani', '₲', 7300.0),
            ('BOB', 'Bolivian Boliviano', 'Bs.', 6.9),
            ('VES', 'Venezuelan Bolívar', 'Bs.S', 36.0),
            ('GYD', 'Guyanese Dollar', 'G$', 209.0),
            ('SRD', 'Surinamese Dollar', '$', 37.5),
            ('TTD', 'Trinidad and Tobago Dollar', 'TT$', 6.8),
            ('JMD', 'Jamaican Dollar', 'J$', 155.0),
            ('BBD', 'Barbadian Dollar', 'Bds$', 2.0),
            ('BSD', 'Bahamian Dollar', 'B$', 1.0),
            ('BZD', 'Belize Dollar', 'BZ$', 2.0),
            ('GTQ', 'Guatemalan Quetzal', 'Q', 7.8),
            ('HNL', 'Honduran Lempira', 'L', 24.7),
            ('NIO', 'Nicaraguan Córdoba', 'C$', 36.5),
            ('CRC', 'Costa Rican Colón', '₡', 530.0),
            ('PAB', 'Panamanian Balboa', 'B/.', 1.0),
            ('CUP', 'Cuban Peso', '$', 24.0),
            ('DOP', 'Dominican Peso', 'RD$', 56.5),
            ('HTG', 'Haitian Gourde', 'G', 135.0),
            
            # Oceania
            ('FJD', 'Fijian Dollar', 'FJ$', 2.25),
            ('PGK', 'Papua New Guinean Kina', 'K', 3.55),
            ('SBD', 'Solomon Islands Dollar', 'SI$', 8.3),
            ('VUV', 'Vanuatu Vatu', 'Vt', 119.0),
            ('WST', 'Samoan Tala', 'WS$', 2.7),
            ('TOP', 'Tongan Paʻanga', 'T$', 2.35),
            ('XPF', 'CFP Franc', 'Fr', 110.0),
            
            # Additional currencies
            ('MNT', 'Mongolian Tugrik', '₮', 2750.0),
            ('KPW', 'North Korean Won', '₩', 900.0),
            ('BND', 'Brunei Dollar', 'B$', 1.35),
            ('MOP', 'Macanese Pataca', 'P', 8.05),
        ]

        created_count = 0
        updated_count = 0
        
        self.stdout.write('Starting worldwide currency population...')
        
        for currency_data in world_currencies:
            if len(currency_data) == 6:
                code, name, symbol, rate, name_english, name_farsi = currency_data
            else:
                # Fallback for currencies without Farsi names
                code, name, symbol, rate = currency_data
                name_english = name
                name_farsi = name
            currency, created = Currency.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'name_english': name_english,
                    'name_farsi': name_farsi,
                    'symbol': symbol,
                    'exchange_rate': Decimal(str(rate)),
                    'is_active': True,
                    'is_default': False,
                    'is_popular': code in ['USD', 'EUR', 'GBP', 'AFN', 'IRR', 'PKR', 'INR', 'AED', 'SAR', 'TRY']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created: {code}')
            else:
                # Update existing currency if needed
                updated = False
                if currency.name != name:
                    currency.name = name
                    updated = True
                if currency.name_english != name_english:
                    currency.name_english = name_english
                    updated = True
                if currency.name_farsi != name_farsi:
                    currency.name_farsi = name_farsi
                    updated = True
                if currency.symbol != symbol:
                    currency.symbol = symbol
                    updated = True
                if currency.exchange_rate != Decimal(str(rate)):
                    currency.exchange_rate = Decimal(str(rate))
                    updated = True
                    
                if updated:
                    currency.save()
                    updated_count += 1
                    self.stdout.write(f'Updated: {code}')
                else:
                    self.stdout.write(f'Exists: {code}')
        
        # Ensure USD is set as default if no default exists
        if not Currency.objects.filter(is_default=True).exists():
            usd_currency = Currency.objects.filter(code='USD').first()
            if usd_currency:
                usd_currency.is_default = True
                usd_currency.save()
                self.stdout.write('Set USD as default currency')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated currencies: {created_count} created, {updated_count} updated'
            )
        )
        self.stdout.write(f'Total currencies in database: {Currency.objects.count()}')
