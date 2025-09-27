# Style keywords, palettes and shop domains per country for query building
STYLE_KEYWORDS = {
    "minimalistisch": ["clean", "unstructured", "straight"],
    "casual": ["denim", "soft", "relaxed"],
    "klassiek": ["oxford", "chino", "tailored"],
    "sportief": ["tech", "stretch", "jogger"],
    "creatief": ["pattern", "color-pop", "statement"]
}

DEFAULT_PALETTES = {
    "minimalistisch": ["black", "white", "navy", "grey", "stone"],
    "casual": ["navy", "olive", "white", "grey", "denim"],
    "klassiek": ["navy", "camel", "white", "light blue", "grey"],
    "sportief": ["black", "charcoal", "white", "cobalt"],
    "creatief": ["navy", "rust", "sage", "cream", "ink"]
}

CURRENCY_BY_COUNTRY = {
    "NL": "EUR", "BE": "EUR", "DE": "EUR", "FR": "EUR", "ES": "EUR", "IT": "EUR",
    "UK": "GBP", "GB": "GBP", "US": "USD", "IE": "EUR", "SE": "SEK"
}

COUNTRY_SHOPS = {
    "NL": ["zalando.nl", "aboutyou.nl", "wehkamp.nl", "hm.com", "decathlon.nl", "uniqlo.com"],
    "BE": ["zalando.be", "aboutyou.be", "debijenkorf.be", "hm.com", "decathlon.be"],
    "DE": ["zalando.de", "aboutyou.de", "hm.com", "otto.de", "uniqlo.com"],
    "FR": ["zalando.fr", "hm.com", "laredoute.fr", "decathlon.fr"],
    "UK": ["zalando.co.uk", "hm.com", "johnlewis.com", "next.co.uk", "uniqlo.com"],
    "US": ["amazon.com", "nordstrom.com", "gap.com", "uniqlo.com", "macys.com"]
}

# Minimal demo catalog to ensure the app works without external APIs
DEMO_FALLBACK_ITEMS = [
    # outer
    {"category": "outer", "title": "Navy overshirt (demo)", "price": 55, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "male", "styles": ["casual", "minimalistisch"], "color": "navy"},
    {"category": "outer", "title": "Cream blazer (demo)", "price": 65, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "female", "styles": ["klassiek", "minimalistisch"], "color": "cream"},
    {"category": "outer", "title": "Black track jacket (demo)", "price": 45, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "unisex", "styles": ["sportief"], "color": "black"},

    # top1
    {"category": "top1", "title": "Light blue oxford shirt (demo)", "price": 35, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "male", "styles": ["klassiek", "casual"], "color": "light blue"},
    {"category": "top1", "title": "Merino sweater grey (demo)", "price": 40, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "unisex", "styles": ["minimalistisch", "klassiek"], "color": "grey"},
    {"category": "top1", "title": "Blouse cream (demo)", "price": 30, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "female", "styles": ["klassiek", "minimalistisch"], "color": "cream"},

    # top2
    {"category": "top2", "title": "Crewneck navy (demo)", "price": 28, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "unisex", "styles": ["casual", "minimalistisch"], "color": "navy"},
    {"category": "top2", "title": "Henley white (demo)", "price": 22, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "male", "styles": ["casual"], "color": "white"},
    {"category": "top2", "title": "Knit sweater sage (demo)", "price": 32, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "female", "styles": ["creatief", "klassiek"], "color": "sage"},

    # bottom
    {"category": "bottom", "title": "Stretch chino olive (demo)", "price": 45, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "male", "styles": ["casual", "klassiek"], "color": "olive"},
    {"category": "bottom", "title": "High-rise trousers camel (demo)", "price": 48, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "female", "styles": ["klassiek"], "color": "camel"},
    {"category": "bottom", "title": "Black joggers (demo)", "price": 35, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "unisex", "styles": ["sportief"], "color": "black"},

    # shoes
    {"category": "shoes", "title": "Lightweight sneakers white (demo)", "price": 30, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "unisex", "styles": ["casual", "sportief"], "color": "white"},
    {"category": "shoes", "title": "Leather loafers cognac (demo)", "price": 55, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "male", "styles": ["klassiek"], "color": "cognac"},
    {"category": "shoes", "title": "Minimal sneakers black (demo)", "price": 40, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "unisex", "styles": ["minimalistisch"], "color": "black"},

    # tee
    {"category": "tee", "title": "Heavy cotton tee white (demo)", "price": 12, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "unisex", "styles": ["casual", "minimalistisch"], "color": "white"},
    {"category": "tee", "title": "Heavy cotton tee black (demo)", "price": 12, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "unisex", "styles": ["minimalistisch"], "color": "black"},

    # accessory
    {"category": "accessory", "title": "Leather belt cognac (demo)", "price": 18, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "male", "styles": ["klassiek", "casual"], "color": "cognac"},
    {"category": "accessory", "title": "Wool scarf navy (demo)", "price": 20, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "unisex", "styles": ["klassiek", "minimalistisch"], "color": "navy"},
    {"category": "accessory", "title": "Beanie grey (demo)", "price": 15, "currency": "EUR", "link": "#", "source": "demo", "thumbnail": None, "gender": "unisex", "styles": ["casual"], "color": "grey"}
]