import logging
from typing import Dict
import gsheets

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ACCOUNTS, DESC, NOMINAL, SUBMIT, DONE = range(5)

def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = [f"{key} : {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [
        ["Salary", "Gifts", "Selling", "Food & Beverages",],
        ["Bills & Utilities", "Transportation", "Shopping"],
        ["Entertainment", "Health & Fitness", "Travelling"],
        ["Gifts & Donation", "Repairs", "Fees & Charges"],
        ["Bond Coupon", "Dividend", "Tax Payments", "Others"],
        ["Capital Gain (Realised)", "Addition to Stock Market"],
        ["Incoming Transfer", "Outgoing Transfer"],
        ["Debt Collection", "Loan Expenditure"],
    ]
    
    print(update.message.chat_id)

    await update.message.reply_text(
        "MONEY MANAGER\n"
        "Send /cancel to stop talking to me.\n\n"
        "What accounts?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return ACCOUNTS


async def desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    text = update.message.text
    context.user_data["input"] = "Accounts"
    column = user_data["input"]
    user_data[column] = text
    del user_data["input"]
    
    await update.message.reply_text(
        f"{facts_to_str(user_data)}\n"
        "Send /cancel to stop talking to me.\n\n"
        "Write the description.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return DESC

async def nominal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    text = update.message.text
    context.user_data["input"] = "Description"
    column = user_data["input"]
    user_data[column] = text
    del user_data["input"]
    
    await update.message.reply_text(
        f"{facts_to_str(user_data)}\n"
        "Send /cancel to stop talking to me.\n\n"
        "How much?",
        reply_markup=ReplyKeyboardRemove(),
    )

    return NOMINAL

async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user_data = context.user_data
    text = update.message.text
    context.user_data["input"] = "Nominal"
    column = user_data["input"]
    user_data[column] = text
    del user_data["input"]
    
    reply_keyboard = [
        ["No", "Yes"],
    ]
    
    if "input" in user_data:
        del user_data["input"]

    await update.message.reply_text(
        f"{facts_to_str(user_data)}\nDo you want to submit?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes or No?"
        ),
    )

    return SUBMIT

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    text = update.message.text
    reply_message = "Your data already submitted." if text == "Yes" else "Submission unsuccessful."
    
    await update.message.reply_text(
        reply_message,
        reply_markup=ReplyKeyboardRemove(),
    )
    
    gsheets.add_data(user_data["Accounts"], "Banknote", user_data["Description"], int(user_data["Nominal"]))

    user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token("6058356935:AAHAcLBn7GO56BJaDSUp_mSBcjPAxQbf5nw").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start, filters=filters.User(1036241047))],
        states={
            ACCOUNTS: [MessageHandler(filters.Regex(
                "^(Salary|Gifts|Selling|Food & Beverages|Bills & Utilities|Transportation|Shopping|Entertainment|Health & Fitness|Travelling|Gifts & Donation|Repairs|Fees & Charges|Bond Coupon|Dividend|Tax Payments|Others|Capital Gain (Realised)|Addition to Stock Market|Incoming Transfer|Outgoing Transfer|Debt Collection|Loan Expenditure)$"), desc)],
            DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, nominal)],
            NOMINAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit)],
            SUBMIT: [MessageHandler(filters.Regex("^(Yes|No)$"), done)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()