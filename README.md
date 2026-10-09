<p align="center">
  <img src="https://raw.githubusercontent.com/iskerwin/ledger-x/main/docs/promo/hero.png" alt="Ledger X" width="100%">
</p>

# Ledger X 演示账本

这是一份**完全虚构**的 [Beancount](https://beancount.github.io) 账本，用来体验 iOS App [**Ledger X**](https://github.com/iskerwin/ledger-x)。它模拟了一位上海上班族从 2025 年 1 月到 2026 年 10 月的日常收支：约 2000 笔交易、每月余额断言、信用卡还款、美股定投、公司报销……App 里的每个功能都能在这里找到对应的数据。

> 想用自己的真实账本？先用这份演示账本熟悉 App，再把 Token 换成你自己的仓库即可。

## 三分钟上手

1. **Fork 本仓库**（右上角 Fork）。建议保持 Public 或改成 Private 都可以，App 只通过你的 Token 访问。
2. **创建 GitHub Token**：GitHub → Settings → Developer settings → Fine-grained tokens → Generate new token
   - Repository access：**Only select repositories** → 选你 fork 出来的 `ledger-demo`
   - Permissions → Contents：**Read and write**
   - Permissions → Actions：**Read-only**（可选，用来在 App 里显示 bean-check 结果）
3. **安装 Ledger X**：从 [Releases](https://github.com/iskerwin/ledger-x/releases/latest) 下载 `Ledger.ipa`，用 SideStore / AltStore 签名安装。
4. **连接**：打开 App，填写用户名（你的 GitHub 用户名）、仓库 `ledger-demo`、分支 `main` 和 Token，点「连接」。

几秒后账本加载完成，就可以开始体验了。在 App 里记的每一笔都会成为这个仓库里的一次 Git 提交，随时可以在 GitHub 上看到改动。

## 推荐体验路线

| 页面 | 试试这些 |
| --- | --- |
| **记账** | 常用交易里点「入账」一键记一笔「瑞幸 拿铁」；手动记一笔支出，看底部实时生成的 Beancount 文本；切到「文本」直接写一条 `price` |
| **概览** | 切换月 / 年、点柱形查看某月；看「支出构成」「商户支出排行」；点「待报销垫款」把最近几笔滴滴打车登记为报销回款 |
| **明细** | 搜索 `#trip-tokyo`、`^refund-618`、`星巴克`、`>1000`、`2025-10`；打开一笔交易「复制为新交易」或「登记退款」 |
| **账户** | 看净资产和资产负债率；打开「招商银行储蓄卡」做一次「余额核对」；左滑某条余额断言试试编辑 / 删除；打开「投资持仓」看 VOO 与 AAPL 的批次和浮动盈亏 |
| **报表** | 损益表切换「本年 / 上年」；资产负债表看净资产走势；试算平衡表；「账本中的查询」运行 `main.bean` 和 `queries/reports.bql` 里预置的查询，再改写一条保存为「我的查询」 |
| **设置** | 换个主题色、切换 English、打开面容 ID 锁定 |

## 账本里有什么

| 场景 | 数据 |
| --- | --- |
| 日常消费 | 早餐、午餐、咖啡（瑞幸 / 星巴克 / Manner）、地铁、打车、周末聚餐、买菜、网购，分别用信用卡、支付宝、微信、现金支付 |
| 固定收支 | 每月工资、房租、电费、话费、iCloud、音乐会员；季度活期利息；2026 年 9 月季度奖金 |
| 信用卡 | 招商银行信用卡每月 10 日全额还款；积分返现 |
| 转账 | 每月给支付宝、微信充值；不定期 ATM 取现（`#transfer`） |
| 外币与投资 | 每季度换汇入金到盈透证券（`@` 汇率，`#fx`）；每月定投 2 股 VOO（按成本 `{}` 记账）；买入、按 FIFO 卖出 AAPL 并结转收益；季度分红 |
| 报销 | 工作日偶尔垫付的客户拜访打车计入 `Assets:Receivable:Reimbursement`，每两个月公司统一报销，用 `#reimbursed ^reimburse-YYYYMMDD` 关联；最近几笔尚未报销 |
| 退款 | 618 购买扫地机器人后的价保退款，用 `^refund-618` 关联 |
| 旅行 | 成都、东京两次旅行的机票和酒店（`#trip-chengdu`、`#trip-tokyo`） |
| 待确认 | 一笔标记为 `!` 的显示器订单 |
| 余额断言 | 每月 1 日核对储蓄卡、支付宝、微信和信用卡余额，全部通过 |
| 价格 | 每两周一次的 USD/CNY 汇率与 VOO、AAPL 股价 |
| 查询 | `main.bean` 中的 `query` 指令，以及 `queries/reports.bql` 中的 5 条常用 BQL |

## 目录结构

```
main.bean                 主文件：选项、include、query 指令
config/commodities.bean   币种与证券
accounts/accounts.bean    开户（含 FIFO 记账方法、账户中文名）
accounts/balance.bean     余额断言
journals/2025.bean        2025 年交易
journals/2026.bean        2026 年交易（App 新记的交易会写在这里）
prices.bean               汇率与股价
queries/reports.bql       常用查询（「-- 标题」作为查询名）
tools/generate.py         生成以上数据的脚本
.github/workflows/        每次推送自动运行官方 bean-check
```

这也是 Ledger X 推荐的仓库结构：交易按年份分文件，余额断言、价格各放一处。App 会自动识别，新的一年会自动创建 `journals/2027.bean` 并在 `main.bean` 中加上 `include`。

## 在电脑上查看

```bash
pip install beancount beanquery fava
bean-check main.bean        # 校验
fava main.bean              # 浏览器打开 http://localhost:5000
```

App 里的报表（损益表、资产负债表、试算平衡表、BQL 查询）与 Fava 的结果一致，可以对照着看。

## 重新生成

演示数据由 `tools/generate.py` 生成，结果固定（随机种子不变）：

```bash
python3 tools/generate.py
```

注意：重新生成会覆盖 `journals/`、`accounts/` 和 `prices.bean`，包括你在 App 里记的内容。想恢复到初始状态时可以这样做，或者直接在 GitHub 上同步上游仓库。

---

所有人名、公司、金额均为虚构，仅供演示。
