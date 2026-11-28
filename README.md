# Ledger X demo ledger

English | [简体中文](README.zh-CN.md)

The single demo data source for the [Ledger X iOS app](https://github.com/iskerwin/ledger-x). Every name, company and amount is made up, there to try out bookkeeping, investments, subscriptions, budgets, salary, personal IOUs and reimbursements.

![Ledger X with this demo ledger open](https://raw.githubusercontent.com/iskerwin/ledger-x/main/docs/promo/gallery.png)

The ledger grew out of the former `ledger-x/Ledger/Demo` and holds **2,037 transactions from 2025-01-01 to 2026-10-17**, 110 balance assertions, 141 price records, and 14 classic examples tagged `#demo-classic`. The data is maintained here from now on; the copy inside the app is no longer kept up.

## Try it in the app

App versions that support the online demo ledger: tap **Try the demo ledger**, and the public data in this repository downloads on first use, with no account or token. After that it can be viewed and edited offline; changes stay on the phone and are never written back here. **Reset the demo** downloads the latest data and, once that succeeds, replaces your local demo changes; if the download fails, the old data is kept. Older app versions still use the demo ledger bundled in the package.

To try real Git sync:

1. Fork this repository to your GitHub account.
2. Create a fine-grained token that can access only that fork, with Contents: Read and write; to see check status, also Actions: Read-only.
3. In the app, connect with your username, repository `ledger-demo`, branch `main` and the token.

Changes in the app are then committed to your fork. Never put the token in ledger files or app source.

## Classic examples to follow along

Search the journal for `#demo-classic`, or pick the saved search 经典示例 (classic examples).

| Scenario | Date and where | What you'll see |
| --- | --- | --- |
| Split payment and partial refunds | Oct 16–17, search `^refund-uniqlo-20261016` | ¥600 list price, ¥450 by credit card and ¥150 by Alipay; two refunds of ¥120 and ¥80 leave ¥400 spent, each refund going back to the account that paid |
| Even split and paying back in parts | Oct 16–17, the personal IOUs page | First pay ¥90 to settle the movie tickets Xiao Chen bought earlier; a ¥480 dinner split three ways counts only ¥160 as your spending. Xiao Chen pays back ¥100 and still owes ¥60; Xiao Lin still owes ¥160 |
| Several advances, reimbursed in batches | Search `^reimburse-shili-20261017` | Hotel ¥680 and train ¥200, settled after two repayments of ¥500 and ¥380; advances and repayments count as neither personal spending nor income |
| Business trip with an open claim | Search `#trip-hangzhou`, event 杭州出差 (Hangzhou trip) | Hotel and train settled; the ¥86 taxi home is still awaiting reimbursement, so you can try recording the repayment |
| Foreign currency subscription | Subscriptions page, GitHub Copilot | 10 USD paid on Oct 16: the charge in its own currency, the CNY conversion and the next renewal |
| Subscription upgrade top-up | Search `^sub-icloud` | A ¥20 top-up on Oct 17 marked `topup: TRUE`, to compare with a normal renewal |
| Trial and manual renewal | Subscriptions page, 效率工具（试用）(productivity tool, trial) | Trial ends Oct 23, ¥38 a month, not yet charged; try the expiry reminder and future cash flow. Reminder state changes with today's date |
| One receipt, two categories | Oct 17, 盒马 (Hema) | Groceries ¥128 and household goods ¥52, one ¥180 Alipay payment split into two expense categories |

## Other data

- **Everyday spending and income**: dining, coffee, commuting, rent, utilities, shopping, medical, red envelopes, charity.
- **Accounts and credit card**: China Merchants Bank, ICBC, cash, Alipay, WeChat; credit card statement day 1, due day 10, limit ¥50,000, with payments and points cashback.
- **Investments**: USD exchange, recurring VOO purchases, buying and selling AAPL, FIFO cost lots, dividends and realized / unrealized gains; prices are made-up history.
- **Salary and employer**: base pay, allowances, withheld income tax, leave deductions, short and back pay, company petty cash.
- **Personal IOUs**: lending, repayments, splits and friends paying for you, told apart by `person:`.
- **Budgets**: dining ¥3,500, shopping ¥1,500, transport ¥600 and subscriptions ¥300 a month.
- **Subscription history**: an iCloud+ price change, NetEase Cloud Music cancelled, Nutstore yearly fee.
- **Travel**: three events, Chengdu, Tokyo and Hangzhou; Tokyo includes JPY spending.
- **To confirm**: a ¥1,699 JD.com monitor on 2026-10-06, flagged `!`.
- **Reports and queries**: income statement, balance sheet, net worth trend, budgets, cash-flow forecast; 2 queries in the main ledger and 5 in a separate file.

## Files

```text
main.bean                   entry point, options, includes and queries
ledger-x.json               app layout, salary template, card number mapping for scanning, saved searches
accounts/accounts.bean      accounts, categories and credit card attributes
accounts/balance.bean       historical balance assertions
config/commodities.bean     CNY / USD / JPY / VOO / AAPL
config/budgets.bean         monthly budgets
config/subscriptions.bean   subscriptions and their change history
config/events.bean          travel and business trip events
journals/2025.bean          2025 transactions
journals/2026.bean          2026 transactions and the classic examples
prices.bean                 historical exchange rates and stock prices
queries/reports.bql         common BQL queries
tools/verify.py             official checks, queries and key example amounts
```

## Checking and maintenance

```bash
uv sync                      # beancount, beanquery, fava from uv.lock
uv run bean-check main.bean
uv run tools/verify.py
uv run fava main.bean
```

Pushes and PRs run the checks automatically. A new example should be checked for balanced postings, historical balance assertions, links and queries, and the walkthrough above updated. New historical transactions can affect later balance assertions, so put new scenarios after the last assertion. Unpaid personal IOUs, open reimbursements and an unconfirmed order are left in the demo on purpose.

The old `tools/generate.py` was removed so that generating old data can't overwrite the budget, subscription, salary and IOU examples. To get the demo data back, fetch this repository again, or reset the demo ledger in the app. Local changes on a phone don't follow updates to the public repository automatically.

## License

[MIT](LICENSE)
