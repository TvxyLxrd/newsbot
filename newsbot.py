import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# здесь указываешь токен своего бота
TOKEN = ''

# здесь указываешь id канала в который публикуешь посты.
CHANNEL_ID = ''

# тут показывается список новостей
news_list = []

# функция, которая получает новости с сайта
def get_news():
    url = 'https://www.rbc.ru'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # логика парсинга
    news_items = soup.find_all('div', class_='news-item')
    for item in news_items:
        title = item.find('h2').text
        content = item.find('p').text
        news_list.append({'title': title, 'content': content})

# обрабатываем команду /start
def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот, который может публиковать новости.")
    get_news()
    show_news(update, context)

# функция, отображающая новости
def show_news(update: Update, context: CallbackContext):
    if not news_list:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Сейчас нет новых новостей.")
        return
    
    news = news_list.pop(0)
    keyboard = [[InlineKeyboardButton("Одобрить", callback_data='approve'),
                InlineKeyboardButton("Удалить", callback_data='delete')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=f"Новость: {news['title']}\n{news['content']}",
                             reply_markup=reply_markup)

# обрабатываем нажатие кнопок
def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == 'approve':
        # публикация новости в канале
        context.bot.send_message(chat_id=update.effective_chat.id, text="Новость одобрена и опубликована в канале.")
    elif query.data == 'delete':
        # удаление новости
        context.bot.send_message(chat_id=update.effective_chat.id, text="Новость удалена.")

# функция публикующая пост
def post_message(update: Update, context: CallbackContext):
    # текст от пользователя
    post_text = ' '.join(context.args)
    
    # проверка
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    try:
        # публикация поста в канал
        context.bot.send_message(chat_id=CHANNEL_ID, text=post_text)
        
        # оповещение, что пост опубликован
        context.bot.send_message(chat_id=update.effective_chat.id, text="Пост успешно опубликован в канале.")
    except Exception as e:
        # обработка ошибок при публикации
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Произошла ошибка при публикации поста: {e}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_click))
    dispatcher.add_handler(CommandHandler("post", post_message))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
