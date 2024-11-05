import sys

sys.path.append(".")
import unittest

from app.agents.tools.exchange_calculate import CurrencyConvertInput, currency_convert_tool


class TestCurrencyConvertTool(unittest.TestCase):
    def test_currency_convert_tool(self):
        amount = 100
        base_currency = "TWD"
        target_currency = "JPY"
        response = currency_convert_tool.run(
            CurrencyConvertInput(amount=amount, base_currency=base_currency, target_currency=target_currency)
        )
        self.assertIsInstance(response.body, str)
        self.assertTrue(response.succeeded)
        print(response)


if __name__ == "__main__":
    unittest.main()
