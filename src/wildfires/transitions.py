# coding: utf-8

from bernard.engine import (
    Tr,
    triggers as trg,
)
from bernard.platforms.telegram.layers import BotCommand

from .states import *
from .triggers import *

transitions = [
    Tr(
        dest=F001xWelcome,
        factory=trg.Equal.builder(BotCommand('/start')),
    ),
    Tr(
        dest=F002xGuess,
        origin=F001xWelcome,
        factory=trg.Action.builder('guess'),
    ),
    Tr(
        dest=E001xInitialize,
        origin=F001xWelcome,
        factory=trg.Action.builder('ok'),
    ),
    Tr(
        dest=F002xGuess,
        origin=E001xInitialize,
        factory=trg.Action.builder('guess'),
    ),
    Tr(
        dest=F003xGuessAgain,
        origin=F002xGuess,
        factory=Bisect.builder(is_right=False),
    ),
    Tr(
        dest=F003xGuessAgain,
        origin=F003xGuessAgain,
        factory=Bisect.builder(is_right=False),
    ),
    Tr(
        dest=F004xCongrats,
        origin=F002xGuess,
        factory=Bisect.builder(is_right=True),
    ),
    Tr(
        dest=F004xCongrats,
        origin=F003xGuessAgain,
        factory=Bisect.builder(is_right=True),
    ),
    Tr(
        dest=F002xGuess,
        origin=F004xCongrats,
        factory=trg.Action.builder('guess'),
    ),
]
