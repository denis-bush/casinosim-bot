#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date as date
import functools
import logging
import redis
import telegram
from telegram.ext import Updater

import decorators
from game import InvalidGameParams
from round import Round, UnacceptableBetError
from games import games
import strings


__package__ = 'casinobot'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TOKEN = '631046420:AAHgOJwxSO8g1-hN9boIJYOC-nPEWKN-mDc'  # old revoked token
ADMIN_USERS = [185809972]
CASINO_CHAT_ID = 303262877

r = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
j = None


def name(value):
    """Fake type that raises ValueError if value does not start with @"""
    if not str(value).startswith('@'):
        raise ValueError
    return str(value)


def get_game(key_or_code):
    try:
        return next(
            filter(lambda g: key_or_code.upper() in (g.key, g.code), games))
    except StopIteration:
        return None


@decorators.command_handler
def antiscam(bot, update, args):
    return strings.antiscam_text


@decorators.command_handler
def chips(bot, update, args):
    username = args[0] if args else update.message.from_user.name
    chips = r.hget('users:{}'.format(username), 'chips')
    if not chips:
        if len(args):
            return '{} non ha chips!'.format(username)
        return '{} non hai chips! Contatta un gestore per fare buy-in'.format(
            username)
    if len(args):
        return '{} ha {} chips'.format(username, chips)
    return '{} hai {} chips'.format(username, chips)


@decorators.command_handler
@decorators.restrict
@decorators.restrict_to_chat
@decorators.args(name, int)
def buyin(bot, update, args):
    name, amount = args[:2]
    balance = r.hincrby('users:{}'.format(name), 'chips', amount)
    logger.info('{} buy-in {}'.format(name, amount))
    message = ('{} {} chips sono state aggiunte al tuo conto!\n'
               'Hai ora {} chips.').format(name, amount, balance)
    return message


@decorators.command_handler
@decorators.restrict_to_chat
@decorators.args(name, int)
def transfer(bot, update, args):
    """Transfer chips"""
    name, amount = args[:2]
    chips = int(
        r.hget('users:{}'.format(update.message.from_user.name), 'chips') or 0)
    if amount > chips:
        return 'Non puoi trasferire chips che non hai ;)'
    if amount <= 0:
        return 'Dai, dona almeno una chip!'
    r.hincrby(
        'users:{}'.format(update.message.from_user.name), 'chips', -amount)
    r.hincrby(
        'users:{}'.format(name), 'chips', amount)
    return '{} hai dato {} delle tue chips a {}. Che gentile!'.format(
        update.message.from_user.name, amount, name)


@decorators.command_handler
@decorators.restrict
def balance(bot, update, args):
    users = r.keys('users:*')
    # build pipeline of all gets, much faster than sending each get alone
    chips = functools.reduce(
        lambda pipe, u: pipe.hget(u, 'chips'), users, r.pipeline()).execute()
    total = 0
    n_with_zero = 0
    message = 'Lista utenti:\n'
    for user, chips in sorted(zip(users, chips), key=lambda x: -int(x[1])):
        if int(chips) == 0:
            n_with_zero += 1
            continue
        message += '{} ha {} chips\n'.format(user.split(':')[1], chips)
        total += int(chips)
    if n_with_zero:
        message += 'Più altri {} giocatori con 0 chips\n'.format(n_with_zero)
    message += '\nTotale: <b>{} ({} monete)</b>'.format(total, total // 100)
    return message


@decorators.command_handler
def info(bot, update, args):
    """
    Returns info about a game
    """
    game = get_game(args[0]) if args else None
    if not game:
        return "Su quale gioco vuoi avere informazioni?"
    return "<b>{}</b>\n{}\n- Puntata minima: {}".format(
        game.code, game.long_description, game.min_bet)


@decorators.command_handler
def list_games(bot, update, args):
    return '\n'.join(
        '<b>[{}] {}</b>: {}'.format(g.key, g.code, g.short_description)
        for g in games)


@decorators.command_handler
@decorators.restrict
@decorators.restrict_to_chat
@decorators.args(name, int)
def buyout(bot, update, args):
    name, amount = args[:2]
    remaining = int(r.hincrby('users:{}'.format(name), 'chips', -amount))
    logger.info('{} buy-out {}'.format(name, amount))
    message = ('{} {} chips sono state tolte dal tuo conto.\n'
               'Ora hai {} chips.').format(name, amount, remaining)
    return message


@decorators.command_handler
@decorators.restrict
@decorators.restrict_to_chat
@decorators.args(int)
def limit(bot, update, args):
    amount = args[0]
    r.hset('config', 'payout_limit', amount)
    return 'Impostato limite vincite round a {}'.format(amount)


@decorators.command_handler
@decorators.args(int, str)
@decorators.restrict_to_chat
def bet(bot, update, args):

    def send_unsent_bet_confirmations(bot):
        message = ''
        current_round = bot.get_current_round(update.message.chat_id)
        if current_round is None:
            return
        to_confirm = current_round.to_confirm_bets
        current_round.to_confirm_bets = []
        for b in to_confirm:
            message += '{} punti {} su {}. Possibile vincita: {}\n'.format(
                b.player.name, b.bet, b.complete_game_name,
                b.predicted_payout)
        message += '\nUsare /annulla per annullare la propria ultima puntata'
        message += '\nPossibile payout rimanente: <b>{}</b>'.format(
            current_round.payout_limit - current_round.total_round_payout)
        bot.reply(update, message)

    current_round = bot.get_current_round(update.message.chat_id)
    amount, game_key_or_code = args[:2]
    game = get_game(game_key_or_code)
    if current_round is None:
        return 'Nessun giro attivo!'
    if current_round.status != 'open':
        return 'Usa /blocca per cambiare le puntate'
    if not game:
        return 'Nessun gioco trovato per: {}'.format(game_key_or_code)
    chips = int(
        r.hget('users:{}'.format(update.message.from_user.name), 'chips') or 0)
    if amount > chips:
        return 'Non hai chips sufficienti per fare questa puntata'
    param = int(args[2]) if len(args) > 2 else None
    try:
        bet = game(update.message.from_user, amount, param)
        current_round.add_bet(bet)
    except (InvalidGameParams, UnacceptableBetError) as e:
        return str(e)
    # all went well
    bet.sent = False
    if j.queue.empty():
        j.put(send_unsent_bet_confirmations, 5, repeat=False)
    r.hincrby(
        'users:{}'.format(update.message.from_user.name), 'chips', -amount)
    logger.info('{} bets {} on {}'.format(
        update.message.from_user.name, amount, bet.complete_game_name))


@decorators.command_handler
@decorators.restrict_to_chat
def cancel(bot, update, args):
    """Cancel the last player bet"""
    current_round = bot.get_current_round(update.message.chat_id)
    if current_round is None:
        return 'Nessun round attivo'
    if current_round.status == 'closing':
        return 'Usa /blocca per cambiare le puntate'
    b = current_round.cancel_last_bet(update.message.from_user)
    if b is None:
        return 'Non hai alcuna puntata da annullare'
    else:
        r.hincrby(
            'users:{}'.format(update.message.from_user.name), 'chips', b.bet)
        return 'Annullata la tua puntata {} su {}.'.format(
            b.bet, b.complete_game_name)


@decorators.command_handler
@decorators.restrict_to_chat
def start_round(bot, update, args):
    """Starts a new round"""
    current_round = bot.get_current_round(update.message.chat_id)
    if current_round is not None:
        return 'C\'è già un round attivo'
    limit = r.hget('config', 'payout_limit')
    limit = int(limit) if limit else None
    new_round = Round(payout_limit=limit)
    bot.set_current_round(update.message.chat_id, new_round)
    return (
        'Inizia un nuovo giro!\n'
        'Massimo payout: <b>{}</b> - Codice antitruffa: <b>{}</b>\nLe puntate'
        ' vengono confermate, in blocchi, qualche secondo dopo').format(
            limit, new_round.proof)


@decorators.command_handler
@decorators.restrict_to_chat
def draw(bot, update, args):
    """Stop bets and schedule draw of a round"""
    current_round = bot.get_current_round(update.message.chat_id)
    if not current_round:
        return 'Nessun giro attivo.'
    if not current_round.bets:
        return 'Aspetta! Nessuno ha ancora puntato in questo round!'
    if current_round.status == 'closing':
        return  # don't send useless message
    # remove bet confirmation send if any
    while not j.queue.empty():
        j.queue.get()
    j.put(lambda b: play_round(b, update, []), 10, repeat=False)
    current_round.status = 'closing'
    message = (
        '<b>Stop alle puntate!</b>\n'
        'Estrazione in 10 secondi, /blocca per bloccare.\n')
    message += '\nPuntate:\n' + '\n'.join(str(b) for b in current_round.bets)
    message += '\n\nPayout <b>{}/{}</b> - antitruffa: <b>{}</b>\n'.format(
        current_round.total_round_payout, current_round.payout_limit,
        current_round.proof)
    return message


@decorators.command_handler
@decorators.restrict_to_chat
def block(bot, update, args):
    """Block draw"""
    current_round = bot.get_current_round(update.message.chat_id)
    if current_round is None or current_round.status != 'closing':
        return 'Non c\'è nessun giro che sta per essere estratto'
    if not j.queue.empty():
        j.queue.get()  # remove from queue
        current_round.status = 'open'
        return 'Estrazione bloccata. Sistemare le puntate e ridare /estrai'


@decorators.command_handler
@decorators.restrict
def force_play_round(bot, update, args):
    play_round(bot, update, args)


def update_stats(bets, draws):

    def get_bet_dict(b, payout, multiplier):
        return {
            'bet': b.bet,
            'payout': payout,
            'multiplier': multiplier,
            'player': b.player.name,
            'game': b.complete_game_name,
        }

    default_best = {'payout': -100, 'multiplier': 0}
    default_worst = {'bet': 0, 'payout': 100000, 'multiplier': 1000}
    best_bet = r.hgetall('betstats:best') or default_best
    luckiest_bet = r.hgetall('betstats:luckiest') or default_best
    worst_bet = r.hgetall('betstats:worst') or default_worst
    unluckiest_bet = r.hgetall('betstats:unluckiest') or default_worst
    total_bet = total_payout = 0
    for bet in bets:
        payout = bet.payout(draws)
        multiplier = (payout / bet.bet) if payout else (bet.multiplier or 5)
        total_bet += bet.bet
        total_payout += payout
        if payout > int(best_bet['payout']):
            best_bet = get_bet_dict(bet, payout, multiplier)
        if payout > 0 and multiplier > float(luckiest_bet['multiplier']):
            luckiest_bet = get_bet_dict(bet, payout, multiplier)
        if multiplier == float(luckiest_bet['multiplier']) and \
           payout > int(luckiest_bet['payout']):
            luckiest_bet = get_bet_dict(bet, payout, multiplier)
        if payout <= int(worst_bet['payout']) and bet.bet > int(worst_bet['bet']):
            worst_bet = get_bet_dict(bet, payout, multiplier)
        if (payout == 0) and (
                multiplier < float(unluckiest_bet['multiplier']) or (
                    multiplier == float(unluckiest_bet['multiplier']) and
                    bet.bet > int(unluckiest_bet['bet'])
                )
        ):
            unluckiest_bet = get_bet_dict(bet, payout, multiplier)

    if best_bet and best_bet != default_best:
        r.hmset('betstats:best', best_bet)
    if luckiest_bet and luckiest_bet != default_best:
        r.hmset('betstats:luckiest', luckiest_bet)
    if worst_bet and worst_bet != default_worst:
        r.hmset('betstats:worst', worst_bet)
    if unluckiest_bet and unluckiest_bet != default_worst:
        r.hmset('betstats:unluckiest', unluckiest_bet)

    r.hincrby(
        'daystats:{}'.format(date.today().isoformat()),
        'total_bet', total_bet)
    r.hincrby(
        'daystats:{}'.format(date.today().isoformat()),
        'total_payout', total_payout)
    r.hincrby('daystats:{}'.format(date.today().isoformat()), 'rounds', 1)
    r.hincrby('allstats', 'total_bet', total_bet)
    r.hincrby('allstats', 'total_payout', total_payout)
    r.hincrby('allstats', 'rounds', 1)


@decorators.command_handler
def play_round(bot, update, args):
    current_round = bot.get_current_round(update.message.chat_id)
    if current_round is None:
        return
    draws = current_round.go()
    message = '\n'.join(
        'Lancio #{}: esce <b>{}</b>!'.format(i+1, d)
        for i, d in enumerate(draws))
    message += '\n\n'
    # Winners
    total_bet = 0
    total_payout = 0
    for bet in current_round.bets:
        total_bet += bet.bet
        payout = bet.payout(draws)
        if payout > 0:
            total_payout += payout
            message += bet.winning_message(draws) + '\n'
            r.hincrby(
                'users:{}'.format(bet.player.name), 'chips', payout)
    update_stats(current_round.bets, draws)
    if total_payout == 0:  # noone won!
        message += 'Nessun vincitore a questo giro! {}\n'.format(
            telegram.Emoji.SEE_NO_EVIL_MONKEY)
    message += '\nTotale giocato: <b>{}</b>\nTotale vinto: <b>{}</b>'.format(
        total_bet, total_payout)
    message += '\nIl seed per il random era: {}'.format(current_round.seed)
    bot.set_current_round(update.message.chat_id, None)
    return message


@decorators.command_handler
def news(bot, update, args):
    return strings.news


@decorators.command_handler
def stats(bot, update, args):

    def str_bet(b):
        if not b:
            return 'nessuna puntata'
        return '{} vince {} puntando {} su {}'.format(
            b['player'], b['payout'], b['bet'], b['game'])

    default = {
        'rounds': 0,
        'total_bet': 0,
        'total_payout': 0,
    }
    daystats = r.hgetall('daystats:{}'.format(date.today().isoformat())) or default
    allstats = r.hgetall('allstats') or default
    best_bet = r.hgetall('betstats:best')
    luckiest_bet = r.hgetall('betstats:luckiest')
    worst_bet = r.hgetall('betstats:worst')
    unluckiest_bet = r.hgetall('betstats:unluckiest')
    message = (
        '<b>Oggi:</b>\n'
        '🍭 Numero giri: {0[rounds]}\n'
        '💸 Totale giocato: {0[total_bet]}\n'
        '💰 Totale vinto: {0[total_payout]}\n\n'
        ''
        '<b>Da quando iniziato a registrare:</b>\n'
        '🍭 Numero giri: {1[rounds]}\n'
        '💸 Totale puntato: {1[total_bet]}\n'
        '💰 Totale vinto: {1[total_payout]}\n\n'
        ''
        '<b>Record puntate:</b>\n'
        '😍 Migliore: {2}\n'
        '🎯 Più fortunata: {3}\n'
        '😭 Peggiore: {4}\n'
        '😡 Più sfortunata: {5}\n\n'
    ).format(daystats, allstats, str_bet(best_bet), str_bet(luckiest_bet),
             str_bet(worst_bet), str_bet(unluckiest_bet))
    return message


class DealerBot(telegram.Bot):

    def __init__(self, token, admin_users, casino_channel=None):
        super(DealerBot, self).__init__(token)
        self.admin_users = admin_users
        self.casino_channel = casino_channel
        self.current_rounds = {}  # active game by chat id

    def get_current_round(self, chat_id):
        return self.current_rounds.get(chat_id, None)

    def set_current_round(self, chat_id, round_):
        self.current_rounds[chat_id] = round_

    def reply(self, update, msg, parse_mode='html'):
        """
        Utility method, easier way to call
        `self.sendMessage(update.message.chat_id, text=msg)`
        """
        try:
            self.sendMessage(
                update.message.chat_id, text=msg, parse_mode=parse_mode)
        except telegram.error.NetworkError as e:
            # we are probably being rate limited, what can we do?
            print(e)


if __name__ == '__main__':
    casinobot = DealerBot(TOKEN, ADMIN_USERS, CASINO_CHAT_ID)
    updater = Updater(bot=casinobot)
    j = updater.job_queue
    dispatcher = updater.dispatcher
    dispatcher.addTelegramCommandHandler('deposita', buyin)
    dispatcher.addTelegramCommandHandler('preleva', buyout)
    dispatcher.addTelegramCommandHandler('trasferisci', transfer)
    dispatcher.addTelegramCommandHandler('chips', chips)
    dispatcher.addTelegramCommandHandler('bilancio', balance)
    dispatcher.addTelegramCommandHandler('punta', bet)
    dispatcher.addTelegramCommandHandler('annulla', cancel)
    dispatcher.addTelegramCommandHandler('limita', limit)
    dispatcher.addTelegramCommandHandler('news', news)
    dispatcher.addTelegramCommandHandler('stats', stats)
    dispatcher.addTelegramCommandHandler('spiega', info)
    dispatcher.addTelegramCommandHandler('lista', list_games)
    dispatcher.addTelegramCommandHandler('giro', start_round)
    dispatcher.addTelegramCommandHandler('estrai', draw)
    dispatcher.addTelegramCommandHandler('blocca', block)
    dispatcher.addTelegramCommandHandler('forza', force_play_round)
    dispatcher.addTelegramCommandHandler('antitruffa', antiscam)
    updater.start_polling()
    updater.idle()
