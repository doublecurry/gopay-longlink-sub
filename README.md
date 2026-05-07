# GPT Plus 支付长链接提取工具 (gopay-longlink-sub)

[](https://www.google.com/search?q=https://github.com/doublecurry/gopay-longlink-sub/blob/main/LICENSE)
[](https://github.com/doublecurry/gopay-longlink-sub/stargazers)

这是一个轻量级的 JavaScript 工具，旨在解决在订阅 ChatGPT Plus 时遇到的支付审批问题。通过获取支付页面的原始长链接（Long Link），帮助用户在支付环境受限或页面跳转失败的情况下完成订阅。

## 🛠️ 主要功能

  * **链接提取**：自动捕获并转换 Stripe 订阅页面的支付长链接。
  * **绕过限制**：解决因浏览器环境导致的 `Payment Approval` 报错。
  * **简洁易用**：通过简单的 JS 脚本即可获取原始 Checkout URL。

## 🚀 使用方法

### 方法一：控制台执行 (Recommended)

1.  登录你的 OpenAI 账户并进入 [ChatGPT 订阅支付页面](https://chatgpt.com/)。
2.  在支付页面（通常是填写信用卡信息的 Stripe 页面）按下 `F12` 打开开发者工具。
3.  切换到 **Console (控制台)** 选项卡。
4.  将本项目中的 [checkout-link-only.js](https://github.com/doublecurry/gopay-longlink-sub/blob/main/checkout-link-only.js) 代码复制并粘贴到控制台中，按回车运行。
5.  脚本将输出提取到的长链接，复制该链接到纯净环境的浏览器中打开即可。

### 方法二：脚本引入

如果你是开发者，可以参考 `gopay-long-link.js` 的实现逻辑集成到你自己的自动化流程中。

## 📂 文件说明

  * `checkout-link-only.js`: 核心脚本，专门用于提取支付链接。
  * `gopay-long-link.js`: 包含更完整的链接处理逻辑。

## ⚠️ 免责声明

  * 本项目仅供技术交流与学习使用。
  * 请确保在操作过程中保护个人隐私及支付卡片信息，不要将生成的支付链接分享给不可信的第三方。
  * 项目作者不对因使用本脚本导致的账号风控或支付损失负责。

## 🤝 贡献

欢迎提交 Issue 或 Pull Request 来改进脚本的兼容性！
