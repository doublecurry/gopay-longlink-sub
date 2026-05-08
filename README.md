# GPT Plus Payment Long Link Extraction Tool (gopay-longlink-sub)

[](https://www.google.com/search?q=https://github.com/doublecurry/gopay-longlink-sub/blob/main/LICENSE)

[](https://github.com/doublecurry/gopay-longlink-sub/stargazers)

This is a lightweight JavaScript tool designed to solve payment approval issues encountered when subscribing to ChatGPT Plus. By obtaining the original long link of the payment page, it helps users complete their subscription even when payment environments are restricted or page redirects fail.

## Main Features

* **Link Extraction**: Automatically captures and converts the long payment link from the Stripe subscription page.

* **Bypassing Restrictions**: Resolves `Payment Approval` errors caused by browser environments.

* **Simple and Easy to Use**: Obtains the original Checkout URL with simple JS scripts.

## Usage Instructions

### Method 1: Console Execution (Recommended)

1. Log in to your OpenAI account and go to the [ChatGPT Subscription Payment Page](https://chatgpt.com/).

2. On the payment page (usually the Stripe page where you fill in your credit card information), press `F12` to open the developer tools.

3. Switch to the **Console** tab.

4. Copy and paste the code from [checkout-link-only.js](https://github.com/doublecurry/gopay-longlink-sub/blob/main/checkout-link-only.js) in this project into the console and press Enter to run it.

5. The script will output the extracted long link. Copy the link and open it in a clean browser environment.

### Method 2: Script Integration

If you are a developer, you can refer to the implementation logic of `gopay-long-link.js` and integrate it into your own automation process.

## Disclaimer

* This project is for technical exchange and learning purposes only.

* Please ensure your personal privacy and payment card information are protected during operation. Do not share the generated payment links with untrusted third parties.

* The project author is not responsible for any account risk control or payment losses resulting from the use of this script.
