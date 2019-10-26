#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, JobQueue
import RPi.GPIO as gpio
import logging
import threading
from time import sleep

BOT_TOKEN = 'YOUR_TOKEN'

AUTH_CODE = 'YOUR_AUTH_CODE'
TRUSTED_USERS = []

MASTER_CODE = 'YOUR_MASTER_PASSWORD'
MASTERS = []

SIGNAL_PORT = 21

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO )
logger = logging.getLogger(__name__)

def usage( update ):
    usage = "Following commands are supported:\n"\
            "/help  - list available commands\n"\
            "/start  - same as above\n"\
            "\n"\
            "/auth   - authenticate (/auth <yourpassword>)\n"\
            "/logout - logout\n"\
            "\n"\
            "/gate   - send command for gate to open/close (depending on current state)\n"\
            "\n"\
            "Commands below are only for advanced use and require master password.\n"\
            "/start_signal - start sending signal and do not stop\n"\
            "/stop_signal  - stop sending signal\n"
    update.message.reply_text( usage )

def command_to_gate():
    gpio.output(SIGNAL_PORT, gpio.HIGH)
    sleep(1.5)
    gpio.output(SIGNAL_PORT, gpio.LOW)

def help(bot, update):
    usage(update)

def check_auth(bot, update, master_cmd):
    """Check is user is among trusted authorized users"""
    id = update.message.from_user['id']

    if id in MASTERS:
        return True
    elif (id in TRUSTED_USERS) and not master_cmd:
        return True

    # Not authorized
    if master_cmd:
        logging.info('Master command attempt from user with no proper rights  '+str(id))
        update.message.reply_text('You have no master rights to execute this command. Use /auth command followed by proper authorization code')
    else:
        logging.info('Insufficient rights for user '+str(id))
        update.message.reply_text('Not authorized. Use /auth command followed by authorization code')
    return False

def start(bot, update):
    """Send a message when the command /start is issued."""
    logging.info('Start command received.')
    update.message.reply_text('Hi! Ready to serve')
    help(bot, update)

def start_signal(bot, update):
    """Send a message when the command /start_signal is issued."""
    logging.info("start_signal command received.")
    if check_auth(bot, update, True):
        update.message.reply_text('Sending command to gate...')
        gpio.output(SIGNAL_PORT, gpio.HIGH)

def stop_signal(bot, update):
    """Send a message when the command /stop_signal is issued."""
    logging.info('stop_signal command received.')
    if check_auth(bot, update, True):
        update.message.reply_text('Sending command to gate...')
        gpio.output(SIGNAL_PORT, gpio.LOW)

def auth(bot, update):
    """Send a message when the command /auth is issued."""
    id = update.message.from_user['id']

    # code starts after '/auth ' - 6 symbols
    code = update.message.text[6:]
    if (code == AUTH_CODE) and (id not in TRUSTED_USERS):
        update.message.reply_text('You are authorized now')
        logging.info('New authorized user '+str(id))
        TRUSTED_USERS.append( id )
        return
    elif (code == MASTER_CODE) and (id not in MASTERS):
        update.message.reply_text('You are authorized as master now')
        logging.info('New authorized master '+str(id))
        MASTERS.append( id )
        return

    if (id in TRUSTED_USERS) or (id in MASTERS) :
        update.message.reply_text('Already authorized')
        return

    update.message.reply_text('Authorization failed')
    logging.info('Failed auth attempt from user '+str(id)+' with code '+code)

def logout(bot, update):
    """Forget authorized user"""
    done = False
    id = update.message.from_user['id']
    if id in MASTERS:
        MASTERS.remove(id)
        done = True

    if id in TRUSTED_USERS:
        TRUSTED_USERS.remove(id)
        done = True

    if done:
        update.message.reply_text('Logged out')
    else:
        update.message.reply_text('User not found')

def gate(bot, update):
    """Send a message when the command /gate is issued."""
    if check_auth(bot, update, False):
        logging.info('Gate command received.')
        update.message.reply_text('Sending command to gate...')
        t = threading.Thread(target=command_to_gate)
        t.start()

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def msg_handler(bot, update):
    """non-command message handler"""
    usage(update)

def main():
    """Start the bot."""
    # Init GPIO
    gpio.setmode(gpio.BCM)
    gpio.setup(SIGNAL_PORT, gpio.OUT)
    gpio.output(SIGNAL_PORT, gpio.LOW)

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("gate", gate))
    dp.add_handler(CommandHandler("stop_signal", stop_signal))
    dp.add_handler(CommandHandler("start_signal", start_signal))
    dp.add_handler(CommandHandler("auth", auth))
    dp.add_handler(CommandHandler("logout", logout))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, msg_handler))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # test:
    #ctx = JobAssets( friday_messages, friday_stickers, friday_gifs )
    #job_q.run_once(random_msg_job,1, ctx, "friday" )

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
