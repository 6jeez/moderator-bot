from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from filters import IsAdminFilter
from gtts import gTTS
import datetime
import random
import asyncio
import config
import time
import db
import os
from aiogram import Bot, Dispatcher, executor, types
   

bot = Bot(token='(TOKEN)', parse_mode="html")
dp = Dispatcher(bot)


db.CreateUserDB()
db.CreateChatDB()


dp.filters_factory.bind(IsAdminFilter)


async def started(dp):
	await bot.send_message(chat_id=(admin_id), text='✅Бот запущен!')


group_rules = {}


@dp.message_handler(commands=['установить_правила'])
async def set_rules(message: types.Message):
    chat_id = message.chat.id
    if message.reply_to_message and message.reply_to_message.text:
        group_rules[chat_id] = message.reply_to_message.text
        await message.answer("Новые правила установлены")
    else:
        await message.answer("Пожалуйста, ответьте на сообщение с текстом правил командой /установить_правила")


@dp.message_handler(commands=['очистить_правила'])
async def clear_rules(message: types.Message):
    chat_id = message.chat.id
    if chat_id in group_rules:
        del group_rules[chat_id]
        await message.answer("Правила очищены")
    else:
        await message.answer("В этой группе нет установленных правил")


@dp.message_handler(commands=['правила'])
async def show_rules(message: types.Message):
    chat_id = message.chat.id
    if chat_id in group_rules:
        rules = group_rules[chat_id]
        await message.answer(f"Правила группы: {rules}")
    else:
        await message.answer("В этой группе правила не установлены")


@dp.message_handler(commands=['chat'])
async def start_command(message: types.Message):
    chat_id = message.chat.id
    await message.reply(f"Чат ид: {chat_id}")


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    await message.answer(f'Привет, <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>nДобро пожаловать в чат!')
    await message.delete()      


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_link = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    await message.reply(f'Добро пожаловать в модератор бот, {user_link}, я помогу управлять вашей группой! Добавь меня в группу чтобы я мог помогать вашей группе. Узнать команды - /хелп', parse_mode='HTML')


@dp.message_handler(content_types=["left_chat_member"])
async def left_member(message: types.Message):
    user_link = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    await message.reply(f'Пока, {user_link}!😔', parse_mode='HTML') 
    await message.delete()


@dp.message_handler(commands='хелп')
async def commands(message):
    await message.reply(f'Для новичков:\n/start - регистрация в боте\n/help - команды\n\nДля модераторов чата:\n/репорт - репорт админам чата (работает только в супергруппе)\n+ - повысить репутацию\n- - понизить репутацию\nБот - проверка работы бота\n/правила - покажет правила чата\n/установить_правила (текст) - установит правила чата\n/очистить_правила - очистит правила чата\n/chat - узнать айди чата\n/mute, /мут (время) (д,дней,день,ч,часов,час,м,минут,минуты) (причина) - замутить пользователя\n/размут, /unmute - размутить пользователя\n/бан, /ban (только навсегда) (причина) - забанить пользователя\n/разбан, /unban - разбанить пользователя\n\nИгровые команды:\n/профиль, /п, /profile, /p - профиль пользователя\n/работа, /work - работать (получить деньги)\n/дать, /give - передать деньги\n/топ, /top - топ по деньгам')


@dp.message_handler(lambda msg: msg.text.lower() == 'бот')
async def check_bot(message):
    await message.reply('✅Бот работает!')


@dp.message_handler(commands=['мут', 'mute'], commands_prefix='!?./', is_chat_admin=True)
async def mute(message):
   if not message.reply_to_message:
      await message.reply("Эта команда должна быть ответом на сообщение!")
      return
   try:
      muteint = int(message.text.split()[1])
      mutetype = message.text.split()[2]
      comment = " ".join(message.text.split()[3:])
   except IndexError:
      await message.reply('Не хватает аргументов!\nПример:\n<code>/мут 1 ч причина</code>')
      return
   if mutetype == "ч" or mutetype == "часов" or mutetype == "час":
      await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date=datetime.timedelta(hours=muteint))
      await message.reply(f'👤Администратор: <a href="tg://?id={message.from_user.id}">{message.from_user.first_name}</a>\n🛑Замутил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n⏰Срок: {muteint} {mutetype}\n📃Причина: {comment}')
   if mutetype == "м" or mutetype == "минут" or mutetype == "минуты":
      await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date=datetime.timedelta(minutes=muteint))
      await message.reply(f'👤Администратор: <a href="tg://?id={message.from_user.id}">{message.from_user.first_name}</a>\n🛑Замутил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n⏰Срок: {muteint} {mutetype}\n📃Причина: {comment}')
   if mutetype == "д" or mutetype == "дней" or mutetype == "день":
      await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date=datetime.timedelta(days=muteint))
      await message.reply(f'👤Администратор: <a href="tg://?id={message.from_user.id}">{message.from_user.first_name}</a>\n🛑Замутил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n⏰Срок: {muteint} {mutetype}\n📃Причина: {comment}')


@dp.message_handler(commands=['размут', 'unmute'], commands_prefix='!?./', is_chat_admin=True)
async def unmute(message):
   if not message.reply_to_message:
      await message.reply("Эта команда должна быть ответом на сообщение!")
      return
   await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(True, True, True, True))
   await message.reply(f'👤Администратор: <a href="tg://?id={message.from_user.id}">{message.from_user.first_name}</a>\n🔊Размутил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>')


@dp.message_handler(commands=['ban', 'бан', 'кик', 'kick'], commands_prefix='!?./', is_chat_admin=True)
async def ban(message):
   if not message.reply_to_message:
      await message.reply("Эта команда должна быть ответом на сообщение!")
      return
   comment = " ".join(message.text.split()[1:])
   await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False))
   await message.reply(f'👤Администратор: <a href="tg://?id={message.from_user.id}">{message.from_user.first_name}</a>\n🛑Забанил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n⏰Срок: навсегда\n📃Причина (если есть): {comment}')


@dp.message_handler(commands=['разбан', 'unban'], commands_prefix='!?./', is_chat_admin=True)
async def unban(message):
   if not message.reply_to_message:
      await message.reply("Эта команда должна быть ответом на сообщение!")
      return
   await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(True, True, True, True))
   await message.reply(f'👤Администратор: <a href="tg://?id={message.from_user.id}">{message.from_user.first_name}</a>\n📲Разбанил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>')


@dp.message_handler(lambda msg: msg.text.lower().startswith('+'))
async def plus_rep(message):
   if not message.reply_to_message:
      await message.reply("Эта команда должна быть ответом на сообщение!")
      return
   if message.from_user.id == message.reply_to_message.from_user.id:
      await message.reply("А нельзя накручивать себе репутацию!🖕")
      return
   db.UpdateUserValue('reputation', 1, message.reply_to_message.from_user.id)
   db.con.commit()
   await message.reply("Повышение репутации засчитано👍")


@dp.message_handler(lambda msg: msg.text.lower().startswith('-'))
async def minus_rep(message):
   if not message.reply_to_message:
      await message.reply("Эта команда должна быть ответом на сообщение!")
      return
   if message.from_user.id == message.reply_to_message.from_user.id:
      await message.reply("А нельзя накручивать себе репутацию!🖕")
      return
   db.UpdateUserValueMinus('reputation', 1, message.reply_to_message.from_user.id)
   db.con.commit()
   await message.reply("Понижение репутации засчитано👎")


@dp.message_handler(commands=['work', 'работа'], commands_prefix='!?./')
async def work(message):
    new_money = random.randint(0, 500)
    db.UpdateUserValue('money', new_money, message.from_user.id)
    db.con.commit()
    user_link = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    await message.reply(f"{user_link}, Ты заработал {new_money}$🤑", parse_mode='HTML')


@dp.message_handler(commands=['дать', 'give'], commands_prefix='!?./')
async def give_money(message):
   if not message.reply_to_message:
      await message.reply('Эта команда должна быть ответом на сообщение!')
      return
   try:
      mtransfer = int(message.text.split()[1])
   except:
      await message.reply("Неверно указаны аргументы!nПример:n/дать 100")
      return
   if mtransfer < 0:
      await message.reply("А минусы нельзя!😶")
      return
   for row in db.cursor.execute(f"SELECT money FROM users where id={message.from_user.id}"):
      if mtransfer > row[0]:
         await message.reply("Не хватает денег!🤑")
         return
   user_to = message.reply_to_message.from_user
   db.UpdateUserValueMinus('money', mtransfer, message.from_user.id)
   db.UpdateUserValue('money', mtransfer, message.reply_to_message.from_user.id)
   db.con.commit()
   await message.reply(f"Вы успешно передали <b>{mtransfer}</b>$ пользователю {user_to.last_name}🤗")


@dp.message_handler(commands=['p', 'п', 'profile', 'профиль'], commands_prefix='!?./')
async def profile(message):
   if not message.reply_to_message:
      for row in db.cursor.execute(f"SELECT reputation, money FROM users where id={message.from_user.id}"):
         await message.reply(f"👤Имя: {message.from_user.first_name}\n🐕Юзернейм: @{message.from_user.username}\n🆔Айди: <code>{message.from_user.id}</code>\n🔝Репутация: {row[0]}\n💸Деньги: {row[1]}$")
   else:
      for row in db.cursor.execute(f"SELECT reputation, money FROM users where id={message.reply_to_message.from_user.id}"):
         await message.reply(f"👤Имя: {message.reply_to_message.from_user.first_name}\n🐕Юзернейм: @{message.reply_to_message.from_user.username}\n🆔Айди: <code>{message.reply_to_message.from_user.id}</code>\n🔝Репутация: {row[0]}\n💸Деньги: {row[1]}$")


@dp.message_handler(commands=['leaderboard', 'top', 'лидеры', 'топ'], commands_prefix='!?./')
async def leaderboard(message):
   db.cursor.execute(f"SELECT name, money FROM users ORDER BY money DESC LIMIT 10")
   leadermsg = "<b>ТОП 10 ПО ДЕНЬГАМ</b>:\n\n"
   fetchleader = db.cursor.fetchall()
   for i in fetchleader:
      leadermsg += f"{fetchleader.index(i) + 1}) {i[0]}:  {i[1]}$\n"
   await message.reply(str(leadermsg))


@dp.message_handler(commands=['стата'], commands_prefix='!?./')
async def stats(message):
   db.cursor.execute("SELECT id FROM users")
   users = db.cursor.fetchall()
   db.cursor.execute(f"SELECT chat_id FROM chats")
   chats = db.cursor.fetchall()
   await message.reply(f'👤 Пользователей в боте: {str(len(users))}\n💬Чатов в боте: {str(len(chats))}')


@dp.message_handler(commands=['userpost', 'юзерпост'], commands_prefix='!?./')
async def userpost(message):
   if message.from_user.id == (admin_id):
      userpost_text = " ".join(message.text.split()[1:])
      db.cursor.execute(f"SELECT id FROM users")
      users_query = db.cursor.fetchall()
      user_ids = [user[0] for user in users_query]
      confirm = []
      decline = []
      await message.reply('Рассылка юзерпоста началась...')
      for user_send in user_ids:
         try:
            await bot.send_message(user_send, userpost_text)
            confirm.append(user_send)
         except:
            decline.append(user_send)
      await message.answer(f'📣 Рассылка юзерпоста завершена!\n\n✅ Успешно: {len(confirm)}\n❌ Неуспешно: {len(decline)}')
   else:
      await message.reply("Недостаточно прав!")


@dp.message_handler(commands=['chatpost', 'чатпост'], commands_prefix='!?./')
async def chatpost(message):
   if message.from_user.id == (admin_id):
      chatpost_text = " ".join(message.text.split()[1:])
      db.cursor.execute(f"SELECT chat_id FROM chats")
      chats_query = db.cursor.fetchall()
      chats_ids = [chat[0] for chat in chats_query]
      confirm = []
      decline = []
      await message.reply('Рассылка чатпоста началась...')
      for chat_send in chats_ids:
         try:
            await bot.send_message(chat_send, chatpost_text)
            confirm.append(chat_send)
         except:
            decline.append(chat_send)
      await message.answer(f'📣 Рассылка чатпоста завершена!\n\n✅ Успешно: {len(confirm)}\n❌ Неуспешно: {len(decline)}')
   else:
      await message.reply("Недостаточно прав!")


@dp.message_handler(commands=['voice', 'войс'], commands_prefix='!?./')
async def voice(message):
   lang_code = os.environ.get("lang_code", "ru")
   cust_lang = None
   voice_text = message.text.split()[1:]
   if len(voice_text) > 200:
      await message.reply("Слишком много символов, не больше 200!")
      return
   try:
      await message.delete()
   except:
      await message.answer("Не могу удалить, пропускаю😬")
   tts = gTTS(voice_text, lang=lang_code)
   tts.save('voice.mp3')
   await bot.send_voice(message.chat.id, open("voice.mp3", "r"), caption=f'Отправитель: <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>')
   os.remove("voice.mp3")


@dp.message_handler(commands=['report', 'репорт'], commands_prefix='!?./')

async def report(message):

   if message.chat.type == '(ссылка)':

      admins_list = [admin.user.id for admin in await bot.get_chat_administrators(chat_id=message.chat.id)]
      report_comment = " ".join(message.text.split()[1:])
      await message.reply("Репорт отправлен!")

      for adm_id in admins_list:

         await bot.send_message(adm_id, text=f'Поступил репорт!\nhttps://t.me/{message.chat.username}/{message.reply_to_message.message_id}\nПричина: <b>{report_comment}</b>')
   else:
      await message.reply("Репорты работают только в супергруппах!")


@dp.message_handler(lambda msg: msg.text.lower() == 'адмкмд')
async def check_bot(message):
    await message.reply('Команды администратора: /юзерпост (пост) - рассылка в бот, /чатпост (пост) - рассылка в чат, /стата - статистика бота')


@dp.message_handler(content_types=['text'])
async def filter_text(message):

   if message.chat.type != 'private':
      db.cursor.execute(f"SELECT chat_name, chat_id FROM chats where chat_id = {message.chat.id}")
      if db.cursor.fetchone() == None:
         db.InsertChatValues(message.chat.title, message.chat.id)

   db.cursor.execute(f"SELECT name FROM users where id = {message.from_user.id}")
   if db.cursor.fetchone() == None:
      db.InsertUserValues(message.from_user.first_name, message.from_user.id)

   if message.chat.type != "private":
      admins_list = [admin.user.id for admin in await bot.get_chat_administrators(chat_id=message.chat.id)]
      if message.from_user.id not in admins_list:
         if '@' in message.text:
            await message.delete()
         for entity in message.entities:
            if entity.type in ["url", "text_link"]:
               await message.delete()


if __name__ == "__main__":
   executor.start_polling(dp, on_startup=started, skip_updates=True)