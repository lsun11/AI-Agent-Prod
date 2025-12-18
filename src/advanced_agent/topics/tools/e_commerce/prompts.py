from ..base_prompts import BaseCSResearchPrompts

class ECommercePrompts(BaseCSResearchPrompts):
    """
    Commerce, payments, and fintech tooling — **shopping or money-first** products.

    Examples:
      - Online marketplaces & storefronts (Shopify, Magento, WooCommerce, BigCommerce)
      - Marketplaces / shopping apps (Amazon, Temu, eBay, Etsy, Shein)
      - Payment processors / gateways (Stripe, Braintree, Adyen)
      - Wallets / P2P payment apps (PayPal, Venmo, Cash App)
      - BNPL / checkout tools (Klarna, Affirm)

    Border rules:
      - If user intent is “how to get paid / pay / shop / checkout” → e_commerce
      - If user intent is “analytics / CRM / ERP for business” → saas
      - Social-first apps with incidental shopping → consumer_and_social
    """

    TOPIC_LABEL = "commerce platform, marketplace app, payment processor, or fintech service"
    ANALYSIS_SUBJECT = (
        "e-commerce platforms, marketplaces, payment systems, wallets, and financial technology tools"
    )
    RECOMMENDER_ROLE = "fintech solutions architect"
