"""
Specific settings for the inventory app.
"""

MIDDLEWARE = [
    "django.contrib.messages.middleware.MessageMiddleware",
]


TEMPLATES = [
    {
        "OPTIONS": {
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
