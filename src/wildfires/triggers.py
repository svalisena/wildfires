from bernard import (
    layers as lyr,
)
from bernard.engine.triggers import (
    BaseTrigger,
)

from .store import (
    cs,
)

import logging
logger = logging.getLogger('bernard.storage.register')

class Bisect(BaseTrigger):
    """
    This trigger will try to interpret when the user reply if he sees the wildfire.
    If it is the string needed, it will use the bisection algorithm to check if it is the beginnig.
    The `is_right` parameter allows to say if you want the trigger to activate
    when the guess is right or not.
    """
    def __init__(self, request, is_right):
        super().__init__(request)
        self.is_right = is_right

    # noinspection PyMethodOverriding
    @cs.inject()
    async def rank(self, context) -> float:
        try:
            if self.request.get_layer(lyr.RawText).text.upper() in ["Y", "YES", "N", "NO"]:
                user_guess = self.request.get_layer(lyr.RawText).text.upper()
            else:
                return .0
        except:
            return .0

        id = self.request.conversation.id
        is_right = False
        if id in context and isinstance(context[id], dict):
            is_right = context[id]['left'] + 1 >= context[id]['right']
            if not is_right:
                if user_guess in ["Y", "YES"]:
                    context[id]['right'] = context[id]['index']
                else:
                    context[id]['left'] = context[id]['index']
                context[id]['index'] = int((context[id]['left'] + context[id]['right']) / 2)

        return 1. if is_right == self.is_right else .0
