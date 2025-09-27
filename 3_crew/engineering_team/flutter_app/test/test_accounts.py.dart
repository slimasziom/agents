```dart
// test/test_accounts.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:accounts/accounts.dart';

void main() {
  group('getSharePrice function', () {
    test('returns correct price for valid symbols', () {
      expect(getSharePrice('AAPL'), 150.0);
      expect(getSharePrice('TSLA'), 700.0);
      expect(getSharePrice('GOOGL'), 2800.0);
    });

    test('returns 0.0 for invalid symbols', () {
      expect(getSharePrice('INVALID'), 0.0);
      expect(getSharePrice(''), 0.0);
    });
  });

  group('Account class', () {
    late Account account;

    setUp(() {
      account = Account('testuser', 10000.0);
    });

    test('initializes with correct values', () {
      expect(account.username, 'testuser');
      expect(account.balance, 10000.0);
      expect(account.initialDeposit, 10000.0);
      expect(account.transactions.isEmpty, true);
      expect(account.holdings.isEmpty, true);
    });

    group('depositFunds', () {
      test('deposits positive amount successfully', () {
        expect(account.depositFunds(500.0), true);
        expect(account.balance, 10500.0);
      });

      test('fails to deposit zero amount', () {
        expect(account.depositFunds(0.0), false);
        expect(account.balance, 10000.0);
      });

      test('fails to deposit negative amount', () {
        expect(account.depositFunds(-100.0), false);
        expect(account.balance, 10000.0);
      });
    });

    group('withdrawFunds', () {
      test('withdraws valid amount successfully', () {
        expect(account.withdrawFunds(1000.0), true);
        expect(account.balance, 9000.0);
      });

      test('fails to withdraw zero amount', () {
        expect(account.withdrawFunds(0.0), false);
        expect(account.balance, 10000.0);
      });

      test('fails to withdraw negative amount', () {
        expect(account.withdrawFunds(-100.0), false);
        expect(account.balance, 10000.0);
      });

      test('fails to withdraw more than balance', () {
        expect(account.withdrawFunds(15000.0), false);
        expect(account.balance, 10000.0);
      });
    });

    group('buyShares', () {
      test('buys shares successfully', () {
        expect(account.buyShares('AAPL', 10), true);
        expect(account.balance, 10000.0 - (150.0 * 10));
        expect(account.holdings['AAPL'], 10);
        expect(account.transactions.length, 1);
        expect(account.transactions.first.type, 'buy');
        expect(account.transactions.first.symbol, 'AAPL');
        expect(account.transactions.first.quantity, 10);
      });

      test('fails to buy shares with insufficient funds', () {
        expect(account.buyShares('GOOGL', 10), false); // Would cost 28000.0
        expect(account.balance, 10000.0);
        expect(account.holdings.containsKey('GOOGL'), false);
        expect(account.transactions.isEmpty, true);
      });

      test('fails to buy zero shares', () {
        expect(account.buyShares('AAPL', 0), false);
        expect(account.balance, 10000.0);
        expect(account.holdings.containsKey('AAPL'), false);
        expect(account.transactions.isEmpty, true);
      });

      test('fails to buy negative shares', () {
        expect(account.buyShares('AAPL', -5), false);
        expect(account.balance, 10000.0);
        expect(account.holdings.containsKey('AAPL'), false);
        expect(account.transactions.isEmpty, true);
      });

      test('buys additional shares of same symbol', () {
        account.buyShares('AAPL', 5);
        expect(account.buyShares('AAPL', 3), true);
        expect(account.holdings['AAPL'], 8);
        expect(account.transactions.length, 2);
      });
    });

    group('sellShares', () {
      setUp(() {
        account.buyShares('AAPL', 20);
      });

      test('sells shares successfully', () {
        expect(account.sellShares('AAPL', 10), true);
        expect(account.holdings['AAPL'], 10);
        expect(account.balance, 10000.0 - (150.0 * 20) + (150.0 * 10));
        expect(account.transactions.length, 2);
        expect(account.transactions.last.type, 'sell');
      });

      test('fails to sell more shares than owned', () {
        expect(account.sellShares('AAPL', 30), false);
        expect(account.holdings['AAPL'], 20);
        expect(account.balance, 10000.0 - (150.0 * 20));
        expect(account.transactions.length, 1);
      });

      test('fails to sell zero shares', () {
        expect(account.sellShares('AAPL', 0), false);
        expect(account.holdings['AAPL'], 20);
        expect(account.balance, 10000.0 - (150.0 * 20));
        expect(account.transactions.length, 1);
      });

      test('fails to sell negative shares', () {
        expect(account.sellShares('AAPL', -5), false);
        expect(account.holdings['AAPL'], 20);
        expect(account.balance, 10000.0 - (150.0 * 20));
        expect(account.transactions.length, 1);
      });

      test('fails to sell shares not owned', () {
        expect(account.sellShares('TSLA', 5), false);
        expect(account.holdings.containsKey('TSLA'), false);
        expect(account.balance, 10000.0 - (150.0 * 20));
        expect(account.transactions.length, 1);
      });

      test('removes symbol from holdings when all shares sold', () {
        expect(account.sellShares('AAPL', 20), true);
        expect(account.holdings.containsKey('AAPL'), false);
        expect(account.balance, 10000.0); // Back to initial balance
        expect(account.transactions.length, 2);
      });
    });

    group('getTotalPortfolioValue', () {
      test('calculates portfolio value with no holdings', () {
        expect(account.getTotalPortfolioValue(), 10000.0);
      });

      test('calculates portfolio value with holdings', () {
        account.buyShares('AAPL', 10);
        account.buyShares('TSLA', 5);
        
        double expectedValue = 10000.0 - (150.0 * 10) - (700.0 * 5) + (150.0 * 10) + (700.0 * 5);
        expect(account.getTotalPortfolioValue(), expectedValue);
      });
    });

    group('getProfitOrLoss', () {
      test('calculates profit/loss with no transactions', () {
        expect(account.getProfitOrLoss(), 0.0);
      });

      test('calculates profit when portfolio value increases', () {
        // Buy shares that appreciate (simulated by holding them)
        account.buyShares('AAPL', 10);
        // Portfolio value should be same as initial since we're just holding
        expect(account.getProfitOrLoss(), 0.0);
      });

      test('calculates loss when portfolio value decreases', () {
        // Withdraw some funds to simulate loss
        account.withdrawFunds(2000.0);
        expect(account.getProfitOrLoss(), -2000.0);
      });
    });

    group('reportHoldings', () {
      test('returns empty holdings initially', () {
        expect(account.reportHoldings().isEmpty, true);
      });

      test('returns correct holdings after purchases', () {
        account.buyShares('AAPL', 15);
        account.buyShares('TSLA', 8);
        
        final holdings = account.reportHoldings();
        expect(holdings.length, 2);
        expect(holdings['AAPL'], 15);
        expect(holdings['TSLA'], 8);
      });
    });

    group('listTransactions', () {
      test('returns empty list initially', () {
        expect(account.listTransactions().isEmpty, true);
      });

      test('returns unmodifiable list of transactions', () {
        account.buyShares('AAPL', 10);
        account.sellShares('AAPL', 5);
        
        final transactions = account.listTransactions();
        expect(transactions.length, 2);
        expect(() => transactions.clear(), throwsA(anything));
      });

      test('transactions have correct properties', () {
        account.buyShares('GOOGL', 2);
        final transaction = account.listTransactions().first;
        
        expect(transaction.type, 'buy');
        expect(transaction.symbol, 'GOOGL');
        expect(transaction.quantity, 2);
        expect(transaction.pricePerShare, 2800.0);
        expect(transaction.date, isA<DateTime>());
      });
    });
  });
}
```