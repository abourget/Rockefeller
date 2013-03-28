import decimal
from collections import namedtuple

from .exchange_rates import get_exchange_rate


def round_amount(amount, currency):
    exponent = '1.' + '0' * currency.exponent
    return amount.quantize(decimal.Decimal(exponent),
                           rounding=decimal.ROUND_HALF_UP)


class Money(namedtuple('Money', 'amount currency')):
    """Representation of money. Each object has an amount and a currency.
    Amount is always converted into a ``decimal``.
    """
    indirection_currency = None

    def __new__(cls, amount, currency):
        if not isinstance(amount, decimal.Decimal):
            amount = round_amount(decimal.Decimal(str(amount)), currency)
        return super(Money, cls).__new__(cls, amount, currency)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.amount == other.amount and self.currency == other.currency)

    def __float__(self):
        return float(self.amount)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        amount = self.amount
        parts = str(amount).split('.')
        if len(parts) == 2 and int(parts[1]) == 0:
            amount = parts[0]
        return u'{}{}'.format(self.currency.symbol, amount)

    def exchange_rate_to(self, currency):
        rate = get_exchange_rate(self.currency, currency)
        if rate is None and Money.indirection_currency:
            rate_from_base = get_exchange_rate(self.currency,
                                               Money.indirection_currency)
            rate_base_to = get_exchange_rate(Money.indirection_currency,
                                             currency)
            if rate_from_base and rate_base_to:
                rate = rate_from_base * rate_base_to

        if rate:
            return rate

    def exchange_to(self, currency):
        rate = self.exchange_rate_to(currency)

        if rate:
            amount = round_amount(self.amount * rate, currency)
            return self.__class__(amount=amount, currency=currency)