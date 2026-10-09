#!/usr/bin/env python3
"""Generate the demo ledger (deterministic). Run from the repo root: python3 tools/generate.py

Everything here is fictional. The script writes:
  main.bean, config/commodities.bean, accounts/accounts.bean, accounts/balance.bean,
  journals/2025.bean, journals/2026.bean, prices.bean
"""
import random, datetime as dt, os, math
from collections import defaultdict

random.seed(20250101)
START = dt.date(2025, 1, 1)
END = dt.date(2026, 10, 8)
NUM_END = 59

def wlen(s):  # display width, CJK counts 2 (matches how the app aligns)
    return sum(2 if ord(c) > 0x2E80 else 1 for c in s)

def amt(n, d=2):
    return f"{n:.{d}f}"

def posting(acct, n=None, ccy="CNY", d=2, extra=""):
    left = "  " + acct
    if n is None:
        return left
    ns = amt(n, d)
    pad = max(2, NUM_END - len(left) - len(ns))
    return left + " " * pad + ns + " " + ccy + (" " + extra if extra else "")

# ---------------------------------------------------------------------------
# ledger state
# ---------------------------------------------------------------------------
txns = []          # (date, text, postings[(acct, n, ccy)])
bal = defaultdict(lambda: defaultdict(float))
lots = []          # IBKR stock lots: [sym, units, cost]

def tx(date, payee, narr, posts, tags="", meta=None, flag="*"):
    """posts: list of (acct, number|None, ccy, extra, d). One None amount = balancing posting."""
    head = f'{date} {flag} "{payee}" "{narr}"' + (" " + tags if tags else "")
    lines = [head]
    for k, v in (meta or {}).items():
        lines.append(f'  {k}: "{v}"')
    weights = defaultdict(float)
    auto = None
    for p in posts:
        acct, n, ccy = p[0], p[1], p[2]
        extra = p[3] if len(p) > 3 else ""
        d = p[4] if len(p) > 4 else 2
        if n is None:
            auto = (acct, ccy)
            lines.append(posting(acct))
            continue
        lines.append(posting(acct, n, ccy, d, extra))
        bal[acct][ccy] += n
        if not extra:
            weights[ccy] += n   # only plain postings are ever auto-balanced here
    if auto:
        acct, ccy = auto
        bal[acct][ccy] -= weights.get(ccy, 0)
    txns.append((date, "\n".join(lines)))

def r(a, b, step=0.1):
    return round(random.uniform(a, b) / step) * step

def days():
    d = START
    while d <= END:
        yield d
        d += dt.timedelta(days=1)

# prices
USD = {}
def usd_rate(d):
    t = (d - START).days
    return round(7.18 + 0.08 * math.sin(t / 70) - 0.0001 * t, 4)
def voo(d):
    t = (d - START).days
    return round(470 + t * 0.14 + 12 * math.sin(t / 40), 2)
def aapl(d):
    t = (d - START).days
    return round(225 + t * 0.06 + 15 * math.sin(t / 30), 2)

# ---------------------------------------------------------------------------
# opening balances
# ---------------------------------------------------------------------------
tx(START, "期初余额", "开账", [
    ("Assets:Bank:CMB", 86000.00, "CNY"),
    ("Assets:Bank:ICBC", 32000.00, "CNY"),
    ("Assets:EWallet:Alipay", 2600.00, "CNY"),
    ("Assets:EWallet:WeChat", 3000.00, "CNY"),
    ("Assets:Cash", 600.00, "CNY"),
    ("Equity:Opening-Balances", None, "CNY"),
])
tx(START, "期初余额", "券商账户开账", [
    ("Assets:Brokerage:IBKR:Cash", 3000.00, "USD"),
    ("Equity:Opening-Balances", None, "USD"),
])

PAY_DAILY = ["Liabilities:CreditCard:CMB"] * 4 + ["Assets:EWallet:Alipay"] * 3 + ["Assets:EWallet:WeChat"] * 3
BREAKFAST = [("全家", "早餐", 9, 16), ("麦当劳", "早餐", 12, 22), ("包子铺", "早餐", 6, 10)]
LUNCH = [("美团外卖", "午餐", 22, 38), ("食堂", "午餐", 15, 22), ("西贝", "午餐", 45, 80), ("沙县小吃", "午餐", 16, 25)]
COFFEE = [("瑞幸", "拿铁", 9.9, 15.9), ("星巴克", "美式", 30, 38), ("Manner", "澳白", 15, 20)]
DINNER = [("海底捞", "晚餐", 180, 320), ("盒马", "晚餐食材", 60, 140), ("美团外卖", "晚餐", 25, 45)]
SHOPPING = [("京东", "日用品", "Expenses:Shopping:Household", 40, 260), ("淘宝", "衣服", "Expenses:Shopping:Clothing", 120, 480),
            ("Apple", "配件", "Expenses:Shopping:Digital", 149, 699), ("宜家", "家居", "Expenses:Shopping:Household", 99, 599)]

unclaimed = []     # (index in txns, amount) of taxi advances not yet reimbursed

d = START
while d <= END:
    wd = d.weekday()
    ds = d.isoformat()
    first = d.day == 1

    # monthly fixed items
    if d.day == 1:
        tx(ds, "房东", "房租", [("Expenses:Housing:Rent", 4500.00, "CNY"), ("Assets:Bank:CMB", -4500.00, "CNY")])
    if d.day == 3:
        tx(ds, "中国联通", "话费", [("Expenses:Subscription:Phone", 59.00, "CNY"), ("Assets:EWallet:Alipay", -59.00, "CNY")])
        tx(ds, "Apple", "iCloud+", [("Expenses:Subscription:Cloud", 21.00, "CNY"), ("Liabilities:CreditCard:CMB", -21.00, "CNY")])
    if d.day == 8:
        n = r(160, 360, 0.01)
        tx(ds, "国家电网", "电费", [("Expenses:Housing:Utilities", n, "CNY"), ("Assets:EWallet:Alipay", -n, "CNY")])
    if d.day == 18:
        tx(ds, "网易云音乐", "会员", [("Expenses:Subscription:Streaming", 15.00, "CNY"), ("Assets:EWallet:WeChat", -15.00, "CNY")])
    if d.day == 25:
        tx(ds, "示例科技有限公司", "工资", [("Assets:Bank:CMB", 26800.00, "CNY"), ("Income:Salary", -26800.00, "CNY")])
    if d.day == 21 and d.month in (3, 6, 9, 12):
        n = r(80, 160, 0.01)
        tx(ds, "招商银行", "活期利息", [("Assets:Bank:CMB", n, "CNY"), ("Income:Invest:Interest", -n, "CNY")])
    if d.day == 26:
        # top up e-wallets from the bank
        tx(ds, "支付宝", "余额充值", [("Assets:EWallet:Alipay", 1500.00, "CNY"), ("Assets:Bank:CMB", -1500.00, "CNY")], tags="#transfer")
        tx(ds, "微信", "零钱充值", [("Assets:EWallet:WeChat", 1200.00, "CNY"), ("Assets:Bank:CMB", -1200.00, "CNY")], tags="#transfer")
    if d.day == 10:
        # repay last month's card spending in full
        owed = -round(bal["Liabilities:CreditCard:CMB"]["CNY"], 2)
        if owed > 0:
            tx(ds, "招商银行信用卡", "还款", [("Liabilities:CreditCard:CMB", owed, "CNY"), ("Assets:Bank:CMB", -owed, "CNY")], tags="#transfer")
    if d.day == 5 and d.month % 4 == 1:
        tx(ds, "ATM", "取现", [("Assets:Cash", 300.00, "CNY"), ("Assets:Bank:ICBC", -300.00, "CNY")], tags="#transfer")

    # investing: quarterly USD funding, monthly VOO, occasional AAPL
    if d.day == 12 and d.month in (1, 4, 7, 10):
        rate = usd_rate(d)
        usd = 5000.00
        tx(ds, "IBKR", "换汇入金", [("Assets:Brokerage:IBKR:Cash", usd, "USD", f"@ {rate:.4f} CNY"),
                                   ("Assets:Bank:CMB", -round(usd * rate, 2), "CNY")], tags="#fx")
    if d.day == 15 and wd < 5 or (d.day in (16, 17) and wd == 0):
        if not any(t[0] == f"{d.year}-{d.month:02d}-VOO" for t in lots):
            px = voo(d)
            tx(ds, "IBKR", "定投 VOO", [("Assets:Brokerage:IBKR:Stock", 2, "VOO", f"{{{px:.2f} USD}}", 0),
                                        ("Assets:Brokerage:IBKR:Cash", -round(2 * px, 2), "USD")])
            lots.append((f"{d.year}-{d.month:02d}-VOO", 2, px))
    if ds in ("2025-02-18", "2025-08-19", "2026-03-17"):
        px = aapl(d)
        tx(ds, "IBKR", "买入 AAPL", [("Assets:Brokerage:IBKR:Stock", 5, "AAPL", f"{{{px:.2f} USD}}", 0),
                                     ("Assets:Brokerage:IBKR:Cash", -round(5 * px, 2), "USD")])
        lots.append(("AAPL-" + ds, 5, px))
    if ds == "2026-07-21":
        px = aapl(d)
        cost = [l for l in lots if l[0].startswith("AAPL")][0][2]
        gain = round(5 * (px - cost), 2)
        tx(ds, "IBKR", "卖出 AAPL", [("Assets:Brokerage:IBKR:Stock", -5, "AAPL", f"{{}} @ {px:.2f} USD", 0),
                                     ("Assets:Brokerage:IBKR:Cash", round(5 * px, 2), "USD"),
                                     ("Income:Invest:Gain", -gain, "USD")])
        bal["Assets:Brokerage:IBKR:Stock"]["AAPL"] += 0  # units tracked by tx()
    if d.day == 28 and d.month in (3, 6, 9, 12):
        n = round(sum(u for k, u, _ in lots if "VOO" in k) * 1.7, 2)
        if n > 0:
            tx(ds, "IBKR", "VOO 分红", [("Assets:Brokerage:IBKR:Cash", n, "USD"), ("Income:Invest:Dividend", -n, "USD")])

    # daily life
    if wd < 5:
        p, nar, a, b = random.choice(BREAKFAST)
        if random.random() < 0.7:
            n = r(a, b)
            acc = random.choice(PAY_DAILY)
            tx(ds, p, nar, [("Expenses:Food:Meals", n, "CNY"), (acc, -n, "CNY")])
        p, nar, a, b = random.choice(LUNCH)
        n = r(a, b)
        tx(ds, p, nar, [("Expenses:Food:Meals", n, "CNY"), (random.choice(PAY_DAILY), -n, "CNY")])
        if random.random() < 0.55:
            p, nar, a, b = random.choice(COFFEE)
            n = r(a, b)
            tx(ds, p, nar, [("Expenses:Food:Drinks", n, "CNY"), (random.choice(PAY_DAILY), -n, "CNY")])
        if random.random() < 0.8:
            n = random.choice([4.00, 5.00, 6.00])
            tx(ds, "地铁", "通勤", [("Expenses:Transit:Metro", n, "CNY"), ("Assets:EWallet:Alipay", -n, "CNY")])
        if random.random() < 0.12:
            # business taxi paid out of pocket, to be reimbursed
            n = r(28, 88)
            tx(ds, "滴滴出行", "客户拜访打车", [("Assets:Receivable:Reimbursement", n, "CNY"), ("Assets:EWallet:Alipay", -n, "CNY")])
            unclaimed.append((len(txns) - 1, n))
    else:
        if random.random() < 0.6:
            p, nar, a, b = random.choice(DINNER)
            n = r(a, b)
            acct = "Expenses:Food:Groceries" if p == "盒马" else "Expenses:Food:Dining"
            tx(ds, p, nar, [(acct, n, "CNY"), (random.choice(PAY_DAILY), -n, "CNY")])
        if random.random() < 0.35:
            n = r(18, 65)
            tx(ds, "滴滴出行", "打车", [("Expenses:Transit:Taxi", n, "CNY"), ("Assets:EWallet:Alipay", -n, "CNY")])
        if random.random() < 0.15:
            n = r(15, 60)
            tx(ds, "菜市场", "买菜", [("Expenses:Food:Groceries", n, "CNY"), ("Assets:Cash", -n, "CNY")])
    if random.random() < 0.09:
        p, nar, acct, a, b = random.choice(SHOPPING)
        n = r(a, b, 0.01)
        tx(ds, p, nar, [(acct, n, "CNY"), ("Liabilities:CreditCard:CMB", -n, "CNY")])

    # reimbursement paid every other month on the 20th, covering advances before the 1st of the month
    if d.day == 20 and d.month % 2 == 0:
        cutoff = d.replace(day=1).isoformat()
        claim = [(i, n) for i, n in unclaimed if txns[i][0] < cutoff]
        if claim:
            link = f"reimburse-{d.strftime('%Y%m%d')}"
            total = round(sum(n for _, n in claim), 2)
            for i, _ in claim:
                date, text = txns[i]
                head, rest = text.split("\n", 1)
                txns[i] = (date, head + f" #reimbursed ^{link}" + "\n" + rest)
            unclaimed = [(i, n) for i, n in unclaimed if txns[i][0] >= cutoff]
            tx(ds, "示例科技有限公司", f"差旅报销 {len(claim)} 笔", [("Assets:Bank:CMB", total, "CNY"),
                                                               ("Assets:Receivable:Reimbursement", -total, "CNY")],
               tags=f"#reimbursed ^{link}")

    # occasional life events
    if ds == "2025-01-28":
        tx(ds, "家人", "春节红包", [("Expenses:Gifts:RedPacket", 2000.00, "CNY"), ("Assets:EWallet:WeChat", -2000.00, "CNY")])
    if ds == "2026-02-16":
        tx(ds, "家人", "春节红包", [("Expenses:Gifts:RedPacket", 2400.00, "CNY"), ("Assets:EWallet:WeChat", -2400.00, "CNY")])
    if ds == "2025-05-01":
        tx(ds, "携程", "机票 上海-成都", [("Expenses:Travel:Flight", 1380.00, "CNY"), ("Liabilities:CreditCard:CMB", -1380.00, "CNY")], tags="#trip-chengdu")
        tx(ds, "全季酒店", "成都 3 晚", [("Expenses:Travel:Hotel", 1047.00, "CNY"), ("Liabilities:CreditCard:CMB", -1047.00, "CNY")], tags="#trip-chengdu")
    if ds == "2025-10-02":
        tx(ds, "携程", "机票 上海-东京", [("Expenses:Travel:Flight", 3260.00, "CNY"), ("Liabilities:CreditCard:CMB", -3260.00, "CNY")], tags="#trip-tokyo")
        tx(ds, "Booking", "东京 5 晚", [("Expenses:Travel:Hotel", 4850.00, "CNY"), ("Liabilities:CreditCard:CMB", -4850.00, "CNY")], tags="#trip-tokyo")
    if ds == "2025-06-18":
        tx(ds, "京东", "扫地机器人", [("Expenses:Shopping:Digital", 2399.00, "CNY"), ("Liabilities:CreditCard:CMB", -2399.00, "CNY")], tags="^refund-618")
    if ds == "2025-06-25":
        tx(ds, "京东", "扫地机器人 价保退款", [("Expenses:Shopping:Digital", -200.00, "CNY"), ("Liabilities:CreditCard:CMB", 200.00, "CNY")], tags="^refund-618")
    if ds in ("2025-04-09", "2025-11-14", "2026-05-20"):
        n = r(120, 480, 0.01)
        tx(ds, "社区医院", "门诊", [("Expenses:Healthcare", n, "CNY"), ("Assets:EWallet:Alipay", -n, "CNY")])
    if ds == "2025-09-10":
        tx(ds, "壹基金", "公益捐赠", [("Expenses:Charity", 200.00, "CNY"), ("Assets:EWallet:Alipay", -200.00, "CNY")])
    if ds in ("2025-03-30", "2025-12-31", "2026-06-30"):
        tx(ds, "招商银行", "信用卡积分返现", [("Liabilities:CreditCard:CMB", 50.00, "CNY"), ("Income:Rewards", -50.00, "CNY")])
    if ds == "2026-09-30":
        tx(ds, "示例科技有限公司", "季度奖金", [("Assets:Bank:CMB", 12000.00, "CNY"), ("Income:Bonus", -12000.00, "CNY")])
    if ds == "2026-10-06":
        tx(ds, "京东", "显示器", [("Expenses:Shopping:Digital", 1699.00, "CNY"), ("Liabilities:CreditCard:CMB", -1699.00, "CNY")], flag="!")

    # month-start balance assertions (computed from the transactions before this day)
    if d.day == 1 and d > START:
        pass
    d += dt.timedelta(days=1)

# ---------------------------------------------------------------------------
# balance assertions: replay transactions in order, assert on the 1st of each month
# ---------------------------------------------------------------------------
ASSERT = ["Assets:Bank:CMB", "Assets:Bank:ICBC", "Assets:EWallet:Alipay", "Assets:EWallet:WeChat", "Liabilities:CreditCard:CMB"]

def parse_amounts(text):
    out = []
    for line in text.split("\n")[1:]:
        p = line.split()
        if len(p) >= 3 and p[0][0].isupper() and ":" in p[0]:
            try:
                out.append((p[0], float(p[1]), p[2]))
            except ValueError:
                pass
    return out

running = defaultdict(float)
balances = []
ti = 0
months = []
m = dt.date(2025, 2, 1)
while m <= END + dt.timedelta(days=1):
    months.append(m)
    m = (m.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
months.append(dt.date(2026, 10, 8))  # a recent check
txns.sort(key=lambda t: t[0] if isinstance(t[0], str) else t[0].isoformat())
txns = [(t[0] if isinstance(t[0], str) else t[0].isoformat(), t[1]) for t in txns]
for m in months:
    ms = m.isoformat()
    while ti < len(txns) and txns[ti][0] < ms:
        for a, n, c in parse_amounts(txns[ti][1]):
            if c == "CNY":
                running[a] += n
        ti += 1
    for a in ASSERT:
        balances.append(f"{ms} balance {a}" + " " * max(1, NUM_END - len(f'{ms} balance {a}') - len(amt(running[a]))) + amt(running[a]) + " CNY")
    if m.day == 1:
        balances.append("")

# ---------------------------------------------------------------------------
# write files
# ---------------------------------------------------------------------------
os.makedirs("journals", exist_ok=True)
os.makedirs("accounts", exist_ok=True)
os.makedirs("config", exist_ok=True)

for year in (2025, 2026):
    body = [t[1] for t in txns if t[0].startswith(str(year))]
    with open(f"journals/{year}.bean", "w") as f:
        f.write(f"; {year} 年交易（演示数据，全部为虚构）\n\n" + "\n\n".join(body) + "\n")

with open("accounts/balance.bean", "w") as f:
    f.write("; 余额断言：每月 1 日核对一次（演示数据）\n\n" + "\n".join(balances).rstrip() + "\n")

accts = set()
for _, text in txns:
    for line in text.split("\n")[1:]:
        p = line.split()
        if p and ":" in p[0] and p[0][0].isupper():
            accts.add(p[0])
NAMES = {
    "Assets:Bank:CMB": "招商银行储蓄卡", "Assets:Bank:ICBC": "工商银行储蓄卡", "Assets:EWallet:Alipay": "支付宝余额",
    "Assets:EWallet:WeChat": "微信零钱", "Assets:Cash": "现金", "Assets:Brokerage:IBKR:Cash": "盈透证券 现金",
    "Assets:Brokerage:IBKR:Stock": "盈透证券 股票", "Assets:Receivable:Reimbursement": "待公司报销的垫款",
    "Liabilities:CreditCard:CMB": "招商银行信用卡",
}
CCY = {"Assets:Brokerage:IBKR:Cash": "USD", "Assets:Brokerage:IBKR:Stock": "VOO,AAPL"}
def section(prefix, title):
    rows = []
    for a in sorted(x for x in accts if x.startswith(prefix)):
        line = f"2025-01-01 open {a}"
        ccy = CCY.get(a, "CNY" if not a.startswith(("Equity", "Income:Invest")) else "")
        if ccy:
            line += " " * max(1, 56 - len(line)) + ccy
        if a == "Assets:Brokerage:IBKR:Stock":
            line += ' "FIFO"'
        rows.append(line)
        if a in NAMES:
            rows.append(f'  name: "{NAMES[a]}"')
    return f"; {title}\n" + "\n".join(rows)
with open("accounts/accounts.bean", "w") as f:
    f.write("\n\n".join([section("Assets", "资产"), section("Liabilities", "负债"), section("Equity", "权益"),
                           section("Income", "收入"), section("Expenses", "支出")]) + "\n")

prices = []
pm = dt.date(2025, 1, 2)
while pm <= END:
    prices.append(f"{pm.isoformat()} price USD" + " " * 10 + f"{usd_rate(pm):.4f} CNY")
    prices.append(f"{pm.isoformat()} price VOO" + " " * 10 + f"{voo(pm):.2f} USD")
    prices.append(f"{pm.isoformat()} price AAPL" + " " * 9 + f"{aapl(pm):.2f} USD")
    pm += dt.timedelta(days=14)
with open("prices.bean", "w") as f:
    f.write("; 每两周一次的价格（演示数据）\n\n" + "\n".join(prices) + "\n")

print(f"{len(txns)} transactions, {len([b for b in balances if b])} balance assertions, {len(prices)} prices")
