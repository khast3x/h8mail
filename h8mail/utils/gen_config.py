# -*- coding: utf-8 -*-
from .colors import colors as c
import os


def gen_config_file():
    with open(
        os.path.join(os.getcwd(), "h8mail_config.ini"), "w", newline=""
    ) as dest_config:
        config = """[h8mail]
; h8mail will automatically detect present keys & launch services accordingly
; Uncomment to activate
;hunterio = 
;snusbase_url = 
;snusbase_token = 
;weleakinfo_priv = 
;weleakinfo_pub = 
;hibp = 
;leak-lookup_pub = 1bf94ff907f68d511de9a610a6ff9263
;leak-lookup_priv =
"""
        dest_config.write(config)
        c.good_news(
            "Generated h8mail template configuration file ({})".format(
                os.path.join(os.getcwd(), "h8mail_config.ini")
            )
        )
