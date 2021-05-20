from lumapps.api.base_client import BaseClient, FileContent  # noqa
from lumapps.api.client import LumAppsClient  # noqa
from lumapps.api.conf import __pypi_packagename__, __version__  # noqa

DEFAULT_KEYS = {
    "keys": [
        {
            "alg": "RS256",
            "e": "AQAB",
            "key_ops": ["verify"],
            "kid": "syn-key-v0",
            "kty": "RSA",
            "n": "vlpsmU3lUoQXKidEwDBcQkWcGTDmBVaP35xaOxY7VaVlEF2-ANFgGxSEux1P0K4gHfwSrovSi8MRMLFbZ_H68SVq1VK7ZU4GQSmaFA_BVJIXHe2s7Szp1_ouylutgKQ0QWjGuYORWbI-9Vsd8i31YCMyka0St2WWxrAYOVhvXtlr4WODJEwZe7lqUo881uFGJi44PJ4-qVPws1hn2BDgm8_PkntcGxLdLpCDE5Nito-GPo24pXQw38AX4rzNR9Q5wlxoDSY9Nar1aDQ0hfQ41heq_BW80tSJGS5SDKPpB6hmCb2-Wv8GxYlwLXbvgiP68hP2xliUJCUfEAg3SP3idndcp54quv8Sdbax-dVSrvMNFhjFyKjNfMCFPk3qOeXXnnO7fsprLxw4dFkmusLWl2XENkEepOiNlMqvuIgX04iuh5-ts_SluNc5Gj9tthbpXU15o1Fd8oZF747SNh_auTLFN3XuXGjJGhin2p7jP33iVFkZdC53ohsmICP1NL5dFD6xKICJo4OUZplzUo9yYsc1sQ2tJRs1SZo_y7Wiiaj9NaGaPBbJjaO6fkOLlYwIkp7ZSKpVfGgNx040DI7s8lTh2e7EDvMiGz8FRwJLAR22h0oIC6tqyhyGFOCA42VqtrX2xPuGMk5sHeeDewBJUKnfKd1mK6_fKQVURJYNJJk",
            "use": "sig",
        }
    ]
}

# flake8: noqa
