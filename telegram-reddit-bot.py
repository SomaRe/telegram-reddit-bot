import logging
import praw
import re
import keys
from telegram import Update
from telegram.ext import Updater, CommandHandler,  CallbackContext
# import os

TOKEN = keys.TELE_TOKEN

# global subred_name, regex, interval
# PORT = int(os.environ.get('PORT', '8443'))
subred_name = "CanadianHardwareSwap"
regex = "[\d]{4,5}"
interval = 30
last_post_time_available = False
last_post_time = 0
new_last_post_time = 0
parameters = ["cpu","gpu","pc","without","rtx"]

reddit = praw.Reddit(
    client_id=keys.reddit_client_id,
    client_secret=keys.reddit_client_secret,
    user_agent="bestdeals",
)


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def help(update: Update, _: CallbackContext):
    update.message.reply_text(''' there are few things to set up before starting search, those are as follows:

Tip: Long press on commands instead of tapping them to edit! 

Use command /subreddit_name <name of subreddit> example: if subreddit is r/funny, give " /subreddit_name funny " as command

Use command /regular_expression <regex> followed by regex in python format (use regex101.com for help). example: " /regular_expression [\d]{3,4} " 

Use command /set_interval <time in seconds> to add how often you want messages?

Use commands /startsearch to start searching and /stop to stop search

Use command /start to restart the bot

Use command /given_subred_name to see the subreddit in action

Use command /given_interval to see the internal set

Use command /given_regex to see the regex given

Use command /add-parameters to add more parameters

Use command /given_parameters to see the parameters given

Use command /delete_parameters to delete all parameters

There are default values for above, but do check spellings and etc if doesn't work!
    ''')

            
def parameter_search(regex,title):
    l = re.findall(regex,title)
    for i in l:
        if(int(i) >= 3000 and int(i) <12000 ):
            return True
    for j in parameters:
        if(title.find(j)!=-1):
            return True
    return False


def get_from_reddit(context: CallbackContext):
    global last_post_time, last_post_time_available, new_last_post_time
    job = context.job
    if(last_post_time_available == False):
        for submission in reddit.subreddit(subred_name).new(limit=None):
            flair = submission.link_flair_text
            if ((flair == "Selling" or flair == "Selling\Trading") and parameter_search(regex,submission.title)):
                last_post_time = submission.created_utc
                last_post_time_available = True
                context.bot.send_message(job.context, text = submission.url)
                break
    else:
        for submission in reddit.subreddit(subred_name).new(limit=None):
            flair = submission.link_flair_text
            post_time = submission.created_utc
            if(post_time > last_post_time):
                new_last_post_time = post_time
                if ((flair == "Selling" or flair == "Selling\Trading") and parameter_search(regex,submission.title)):
                    context.bot.send_message(job.context,text=submission.url)
            else:
                last_post_time = new_last_post_time
                break


def search(update:Update, context: CallbackContext):
    update.message.reply_text("Job started!")
    chat_id = update.message.chat_id
    context.job_queue.run_repeating(get_from_reddit, interval, first=5,context=chat_id)


def start(update: Update, _: CallbackContext):
    update.message.reply_text('Hi! give use command /instructions to see how to set the bot ready for action')

def add_parameters(update:Update, context: CallbackContext):
    global parameters
    for i in range(len(context.args)):
        parameters.append(context.args[i].lower())
    update.message.reply_text("currently available parameters: "+" ".join(parameters) )

def subreddit_name(update:Update, context: CallbackContext):
    global subred_name
    subred_name = context.args[0]
    context.user_data['subred_name'] = subred_name
    update.message.reply_text(f' r/{subred_name} is the subreddit given!')
    

def regular_expression(update:Update, context: CallbackContext):
    global regex 
    regex = context.args[0]
    context.user_data['regex'] = regex
    update.message.reply_text( 'Regular expression given is '+ regex)


def set_interval(update:Update, context: CallbackContext):
    global interval
    interval = context.args[0]
    context.user_data['interval'] = interval
    update.message.reply_text( 'Your set interval is '+ interval)


def stop(update:Update, context: CallbackContext):
    update.message.reply_text( 'Stopping the search!')
    context.job_queue.stop()

def given_subred_name(update:Update, _: CallbackContext):
    update.message.reply_text("Subreddit in action: "+subred_name)

def given_interval(update:Update, _: CallbackContext):
    update.message.reply_text("Interval set: " + str(interval))

def given_regex(update:Update, context: CallbackContext):
    update.message.reply_text("Regex given: "+ regex)

def given_parameters(update:Update, context: CallbackContext):
    update.message.reply_text("given parameters: "+ ", ".join(parameters))

def delete_parameters(update:Update, context: CallbackContext):
    global parameters
    parameters.clear()
    update.message.reply_text("All parameters cleared")

def main():
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start",start))
    dispatcher.add_handler(CommandHandler("subreddit_name",subreddit_name))
    dispatcher.add_handler(CommandHandler("regular_expression", regular_expression))
    dispatcher.add_handler(CommandHandler("set_interval", set_interval))
    dispatcher.add_handler(CommandHandler("add_parameters",add_parameters))
    dispatcher.add_handler(CommandHandler("startsearch",search))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("instructions",help))
    dispatcher.add_handler(CommandHandler("given_subred_name",given_subred_name))
    dispatcher.add_handler(CommandHandler("given_interval",given_interval))
    dispatcher.add_handler(CommandHandler("given_regex",given_regex))
    dispatcher.add_handler(CommandHandler("given_parameters",given_parameters))
    dispatcher.add_handler(CommandHandler("delete_parameters",delete_parameters))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()


