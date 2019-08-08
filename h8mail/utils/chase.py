#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .colors import colors as c


def chase(target, user_args):
    """
    Takes the current target & returns adequate chase list
    to add to the current target list
    """
    new_targets = []
    chase_counter = 0
    if user_args.debug:
        print(c.fg.red, "\nCHASING DEBUG-----------")
        print(f"Hunting targets from {target.target}")
        print(f"Recursive Chase Stop is at {user_args.chase_limit}" + c.reset)
    if user_args.chase_limit > 0:
        for d in target.data:
            if len(d) is not 2:
                continue

            if user_args.power_chase:
                if "RELATED" in d[0]:
                    c.good_news(
                        "Chasing {new_target} as new target".format(new_target=d[1])
                    )
                    new_targets.append(d[1])
            else:
                if "HUNTER_RELATED" in d[0]:
                    c.good_news(
                        "Chasing {new_target} as new target".format(new_target=d[1])
                    )
                    new_targets.append(d[1])
    return new_targets
