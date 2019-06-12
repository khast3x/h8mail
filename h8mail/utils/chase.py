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
    if user_args.chase_limit:
        for d in target.data:
            if len(d) is not 2:
                continue
            if "HUNTER_RELATED" in d:
                c.good_news(
                    "Chasing {new_target} as new target".format(new_target=d[1])
                )
                new_targets.append(d[1])
                chase_counter += 1
            if chase_counter == user_args.chase_limit:
                return new_targets
    return new_targets
