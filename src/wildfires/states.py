# coding: utf-8
from bernard import (
    layers as lyr,
)
from bernard.analytics import (
    page_view,
)
from bernard.engine import (
    BaseState,
)
from bernard.i18n import (
    translate as t,
)
from bernard.platforms.telegram import (
    layers as tgr,
)
from .store import (
    cs,
)
from .initialize import LandsatBisector


class WildfiresState(BaseState):
    """
    Root class for Wildfires.

    This are the default functions called when something goes wrong. The ERROR and
    CONFUSED texts are defined in `i18n/en/responses.csv`.
    """

    @page_view('/bot/error')
    async def error(self) -> None:
        """
        This happens when something goes wrong (it's the equivalent of the
        HTTP error 500).
        """

        self.send(lyr.Text(t.ERROR))

    @page_view('/bot/confused')
    async def confused(self) -> None:
        """
        This is called when the user sends a message that triggers no
        transitions.
        """

        self.send(lyr.Text(t.CONFUSED))

    async def handle(self) -> None:
        raise NotImplementedError


"""
    Classes named as FXXXx... are used to define the main Flow for the bot.
    Classes named as EXXXx... are used to define parallel jobs that need to be done.  
"""


class F001xWelcome(WildfiresState):
    """
    Welcome the user and offer him the posibility to start searching for the
    start of the wildfire
    """

    @cs.inject()
    async def handle(self, context) -> None:
        name = await self.request.user.get_friendly_name()
        if 'shots' not in context:
            self.send(
                lyr.Text(t('INITIALIZE', name=name)),
                tgr.InlineKeyboard([
                    [tgr.InlineKeyboardCallbackButton(
                        text=t.OK,
                        payload={'action': 'ok'},
                    )],
                ])
            )
        else:
            self.send(
                lyr.Text(t('WELCOME', name=name)),
                tgr.InlineKeyboard([
                    [tgr.InlineKeyboardCallbackButton(
                        text=t.LETS_GUESS,
                        payload={'action': 'guess'},
                    )],
                ])
            )


class E001xInitialize(WildfiresState):
    """
    Initialize the images context so the user can start guessing
    """

    @cs.inject()
    async def handle(self, context) -> None:
        context['shots'] = LandsatBisector(-120.70418, 38.32974)
        self.send(
            lyr.Text(text=t.INITIALIZED),
            tgr.InlineKeyboard([
                [tgr.InlineKeyboardCallbackButton(
                    text=t.LETS_GUESS,
                    payload={'action': 'guess'},
                )],
            ])
        )


class F002xGuess(WildfiresState):
    """
    In this state we start the user context and then we show the first image
    so the user can tell if he sees the Wildfire.
    """

    # noinspection PyMethodOverriding
    @cs.inject()
    async def handle(self, context) -> None:
        context[self.request.conversation.id] = {'index': int(context['shots']['count'] / 2),
                                                 'left': 0,
                                                 'right': context['shots']['count']}

        date = context['shots']['shots'][context[self.request.conversation.id]['index']][0]['date']
        url = context['shots']['shots'][context[self.request.conversation.id]['index']][1]

        self.send(
            lyr.RawText(text=url),
            lyr.Text(t('DO_YOU_SEE_IT', date=date))
        )


class F003xGuessAgain(WildfiresState):
    """
    In this state we show the next images to the user and ask again if he sees the
    Wildfire to find the start of it using a bisection algorithm.
    """

    @cs.inject()
    async def handle(self, context) -> None:
        date = context['shots']['shots'][context[self.request.conversation.id]['index']][0]['date']
        url = context['shots']['shots'][context[self.request.conversation.id]['index']][1]

        self.send(
            lyr.RawText(text=url),
            lyr.Text(t('DO_YOU_SEE_IT', date=date))
        )


class F004xCongrats(WildfiresState):
    """
    Congratulate the user for helping the bot to find the start of the wildfire.
    """

    @cs.inject()
    async def handle(self, context) -> None:
        name = await self.request.user.get_friendly_name()
        date = context['shots']['shots'][context[self.request.conversation.id]['index']][0]['date']
        self.send(
            lyr.Text(t('CONGRATULATIONS', name=name, date=date)),
            tgr.InlineKeyboard([
                [tgr.InlineKeyboardCallbackButton(
                    text=t.AGAIN,
                    payload={'action': 'guess'},
                )],
            ])
        )
