# Giveaway Management Bot - Milestone Edition
# Original by @xeltexynos | Modified for Auto Milestones
# Version: 4.0.0

print("Importing Libraries...")
import pyrogram
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram import filters

import random
import database

import os
from datetime import datetime
import asyncio
import varfile

print("Starting Client...")
app = pyrogram.Client(
    name=varfile.bot_username,
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
    bot_token=varfile.bot_token,
)

print("Initializing Configuration...")
if varfile.test_mode:
    print("Test Mode Activated!")
    channel_id = varfile.test_channel_id
    group_id = varfile.test_group_id
else:
    channel_id = varfile.channel_id
    group_id = varfile.group_id

print("Initializing Database...")
if not os.path.exists(varfile.database):
    database.create_db()


class Root:
    def __init__(self, database: database):
        self.database = database
        self.data = self.database.load_db()

    def __getitem__(self, key):
        self.data = self.database.load_db()
        return self.data[key]


root = Root(database=database)


def preliminaries():
    pass


def printlog(message, end=""):
    if end != "":
        print(message, end=end)
    else:
        print(message)

    if not varfile.test_mode:
        current_time = datetime.now().strftime(format="%H:%M:%S")
        current_date = datetime.now().strftime(format="%Y-%m-%d")
        if not os.path.exists(path="logs"):
            os.makedirs(name="logs")
        with open(
            file=(os.path.join("logs", f"{current_date}.log")),
            mode="a+",
            encoding="utf-8",
        ) as log:
            log.write(f"[{current_time}] {message}\n")


async def start_giveaway_auto(client: pyrogram.Client, duration_hours: int = 24):
    """Auto-start a giveaway when a milestone is reached"""
    
    printlog(message=f"Auto-starting milestone giveaway for {duration_hours} hours")
    
    database.set_time(total=duration_hours * 3600, left=0)
    
    try:
        msg = await client.get_messages(chat_id=channel_id, message_ids=root["post_id"])
        
        if msg and msg.caption:
            caption_parts = msg.caption.markdown.split(chr(10))
            await client.edit_message_caption(
                chat_id=channel_id,
                message_id=root["post_id"],
                caption=f"{caption_parts[0]}\n\n"
                        f"🎯 **Milestone Giveaway!** 🎯\n"
                        f"Total Registrations: {len(root['users'])}\n\n"
                        f"⏰ Giveaway ends in {duration_hours} hours!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(
                            text="🎁 Register to Win! 🎁",
                            url=f"https://t.me/{varfile.bot_username}?start=register"
                        )]
                    ]
                )
            )
    except:
        pass
    
    await client.send_message(
        chat_id=group_id,
        text=f"⚡ **GIVEAWAY STARTED!** ⚡\n\n"
             f"🎉 We've reached a milestone!\n"
             f"🏆 A random winner will be selected in {duration_hours} hours!\n\n"
             f"Click the button in our channel to register and win!"
    )


@app.on_message(
    filters=filters.user(users=varfile.admins)
    & filters.private
    & ~filters.command(
        commands=[
            "abort",
            "stats",
            "start",
            "settime",
            "ban",
            "unused",
            "unban",
            "cleardata",
            "setmilestone",
            "checkmilestone",
            "resetmilestone",
            "forceset"
        ]
    )
)
async def poster(client: pyrogram.Client, message: Message):
    printlog(message=f"Message received from {message.from_user.id}!")
    if message.caption:
        printlog(message=f"Sending Post to channel...")
        message_sent = await client.send_photo(
            chat_id=channel_id,
            caption=message.caption.markdown
            + "\n\nTotal Registrations: Please wait...",
            photo=message.photo.file_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Register!",
                            url=f"https://t.me/{varfile.bot_username}?start=register",
                        )
                    ]
                ]
            ),
        )

        printlog(message=f"Setting Post ID...")
        database.set_post_id(post_id=message_sent.id)

        printlog(message=f"Post sent to channel!")
        await message.reply(text="Sent!")

    else:

        if root["post_id"] == None:
            return

        if root["time"]["total"] == 0:
            await message.reply(text="Time not set!")
            return

        printlog(message=f"Collecting Codes...")
        await message.reply(
            text=f"Starting the giveaway in {root['time']['total']/3600} hours, To abort, send /abort"
        )

        printlog(message="Configuring Variables...")
        if message.text != "continue":
            codes = message.text.split(sep="\n")
            database.clear_chosen()
            database.add_codes(codes=codes)
        else:
            codes = root["codes"]

        printlog(message="Starting Timer...")
        zfill_num = len(str(object=root["time"]["total"]))
        total = root["time"]["total"]

        for i in range(round(number=total)):
            print(
                "Time left: " + str(object=total - i).zfill(zfill_num),
                end="\r",
            )

            if (total - i) % 60 == 0:
                database.set_time(total=total, left=total - i)

            await asyncio.sleep(delay=1)

        printlog(message="\nEnding Giveaway...")
        try:
            await client.edit_message_reply_markup(
                chat_id=channel_id, message_id=root["post_id"], reply_markup=None
            )
        except:
            pass

        printlog(message="Choosing Winners...")
        for _ in range(len(codes)):
            while True:
                try:
                    user = await client.get_users(
                        user_ids=random.choice(seq=list(root["users"]))
                    )
                except Exception as e:
                    print(e)
                    continue
                break

            database.mark_chosen(user=user.id)

        printlog(message="Sending Messages...")
        for i in range(len(codes)):
            user = await client.get_users(user_ids=root["chosen"][i])

            await client.send_message(
                chat_id=group_id,
                text=f"{user.mention()}:[{root['chosen'][i]}](tg://user?id={root['chosen'][i]}) click on the button below to receive your present! You have {varfile.auto_abort//3600} hours to do so :D",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Redeem!",
                                url=f"https://t.me/{varfile.bot_username}?start=redeem",
                            )
                        ]
                    ]
                ),
            )

            await asyncio.sleep(delay=30)

        database.clear_post_id()

        printlog(message="Sending Winner List...")
        users = await client.get_users(user_ids=root["chosen"])
        msg = await client.send_message(
            chat_id=group_id,
            text="Giveaway has ended! List of winners: \n"
            + "\n".join([f"{x.mention()}:{x.id}" for x in users])
            + "\n\nBot by @XelteXynos",
        )
        await client.pin_chat_message(chat_id=group_id, message_id=msg.id)

        printlog(message="Starting Timer...\n")
        zfill_num = len(str(object=varfile.auto_abort))
        for i in range(int(varfile.auto_abort)):
            print(
                "Time left: " + str(object=varfile.auto_abort - i).zfill(zfill_num),
                end="\r",
            )
            await asyncio.sleep(delay=1)

        printlog(message="\nCollecting Unused Codes...")
        await message.reply(
            text="Unused Codes:\n\n"
            + "\n".join([x for x in root["codes"] if x not in root["used_codes"]])
        )

        database.snapshot()
        database.clear_db()
        printlog(message="Bot has been reset!")


@app.on_message(
    filters=filters.command(commands="start", prefixes="/") & filters.private
)
async def start(client: pyrogram.Client, message: Message):
    if len(message.command) == 1:
        await message.reply(
            text=f"🎁 **Milestone Giveaway Bot** 🎁\n\n"
                 f"Welcome to Top Tokens Official!\n\n"
                 f"Use the button below to register for giveaways when we hit milestones!\n\n"
                 f"🔹 50 members - 5 TON Giveaway\n"
                 f"🔹 100 members - 10 TON Giveaway\n"
                 f"🔹 200 members - 20 TON Giveaway\n"
                 f"🔹 500 members - 50 TON Giveaway\n\n"
                 f"Made by @XelteXynos | Modified for Top Tokens"
        )
        return

    if message.command[1] == "register":
        if (
            root["post_id"] == None
            or message.from_user.id in root["chosen"]
            or message.from_user.id in root["banned"]
            or message.from_user.id in root["users"]
        ):
            return

        printlog(message=f"Registering {message.from_user.id}...")

        if message.from_user.id not in root["users"]:
            database.add_user(user=message.from_user.id)
            
            current_count = len(root["users"])
            
            if hasattr(varfile, 'milestones') and varfile.milestones:
                try:
                    if varfile.next_milestone_index < len(varfile.milestones):
                        next_milestone = varfile.milestones[varfile.next_milestone_index]
                        
                        if current_count >= next_milestone and not varfile.milestone_reached:
                            varfile.milestone_reached = True
                            
                            await client.send_message(
                                chat_id=group_id,
                                text=f"🎉 **MILESTONE ACHIEVED!** 🎉\n\n"
                                     f"We've reached {current_count} members in Top Tokens Official!\n\n"
                                     f"🏆 **GIVEAWAY TIME!** 🏆\n"
                                     f"A random winner will be selected from registered users!\n\n"
                                     f"Click the button in our channel to register and win!",
                            )
                            
                            await start_giveaway_auto(client, duration_hours=24)
                            
                            varfile.next_milestone_index += 1
                            varfile.milestone_reached = False
                except Exception as e:
                    printlog(f"Milestone check error: {e}")

            if len(root["users"]) % 10 == 0:
                try:
                    msg = await client.get_messages(
                        chat_id=channel_id, message_ids=root["post_id"]
                    )
                    
                    if msg and msg.caption:
                        caption_lines = msg.caption.markdown.split("\n")
                        if len(caption_lines) >= 1:
                            await client.edit_message_caption(
                                chat_id=channel_id,
                                message_id=root["post_id"],
                                caption=f"{caption_lines[0]}\n\nTotal Registrations: {len(root['users'])}",
                                reply_markup=InlineKeyboardMarkup(
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(
                                                text="Register!",
                                                url=f"https://t.me/{varfile.bot_username}?start=register",
                                            )
                                        ]
                                    ]
                                ),
                            )
                except Exception as e:
                    printlog(f"Channel update error: {e}")

                if varfile.group_stats:
                    await client.send_message(
                        chat_id=group_id,
                        text=f"📊 {len(root['users'])} users have registered!\n\n[Click here if you haven't registered yet!](https://t.me/{varfile.bot_username}?start=register)",
                    )

            printlog(message=f"User {str(object=message.from_user.id)} has registered!")

            await message.reply(text="✅ You're registered for the giveaway!")

    elif message.command[1] == "redeem":

        if message.from_user.id not in root["chosen"]:
            await message.reply(text="❌ You haven't won any giveaway yet!")
            return

        code = root["codes"][root["chosen"].index(message.from_user.id)]

        if code not in root["used_codes"]:
            await message.reply(
                text=f"🎉 **You've won!** 🎉\n\nHere's your prize code: `{code}`\n\nRedeem it before it expires!"
            )

            database.mark_used(code=code)

            try:
                printlog(
                    message=f"{code} has been redeemed by {message.from_user.first_name}"
                )
            except:
                printlog(message=f"{code} has been redeemed by {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="cleardata", prefixes="/")
    & filters.private
    & filters.user(users=varfile.admins)
)
async def cleardata(_, message: Message):
    printlog(message=f"Clearing data on command of {message.from_user.id}...")
    database.clear_db()
    await message.reply(text="✅ Data cleared!")
    printlog(message=f"Data cleared on command of {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="unused", prefixes="/")
    & filters.private
    & filters.user(users=varfile.admins)
)
async def unused(_, message: Message):
    printlog(message=f"Sending unused codes to {message.from_user.id}...")
    unused_codes = [x for x in root["codes"] if x not in root["used_codes"]]

    if len(unused_codes) == 0:
        await message.reply(text="No unused codes!")
        return

    await message.reply(text="Unused Codes:\n\n" + "\n".join(unused_codes))

    printlog(message=f"Unused codes sent to {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="abort", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def abort(_, message: Message):
    await message.reply(text="⚠️ Giveaway aborted!")
    printlog(message=f"Bot has been aborted on command of {message.from_user.id}")
    quit()


@app.on_message(
    filters=filters.command(commands="stats", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def stats(_, message: Message):
    printlog(message=f"Sending stats to {message.from_user.id}...")
    
    milestone_status = "No milestones set"
    if hasattr(varfile, 'milestones') and varfile.milestones:
        if varfile.next_milestone_index < len(varfile.milestones):
            next_milestone = varfile.milestones[varfile.next_milestone_index]
            milestone_status = f"Next: {next_milestone} (Need {next_milestone - len(root['users'])} more)"
        else:
            milestone_status = "All milestones completed! 🎉"

    await message.reply(
        text=f"📊 **Giveaway Stats**\n\n"
             f"⏰ Time: {root['time']['left']}/{root['time']['total']}\n"
             f"👥 Users: {len(root['users'])}\n"
             f"🎫 Codes: {len(root['codes'])}\n"
             f"🏆 Chosen: {len(root['chosen'])}\n"
             f"🚫 Banned: {len(root['banned'])}\n"
             f"✅ Used Codes: {len(root['used_codes'])}\n"
             f"📝 Post ID: {root['post_id']}\n\n"
             f"🎯 {milestone_status}"
    )

    printlog(message=f"Stats sent to {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="settime", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def settime(_, message: Message):
    try:
        printlog(f"Setting time to {message.command[1]} hours...")
        database.set_time(total=int(float(message.command[1]) * 3600), left=0)
        printlog(f"Time set to {root['time']['total']/3600} hours!")
        await message.reply(f"✅ Giveaway duration set to {message.command[1]} hours!")
    except:
        await message.reply("❌ Invalid Time! Use: /settime 24")


@app.on_message(
    filters=filters.command(commands="ban", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def ban(client: pyrogram.Client, message: Message):
    printlog(f"Banning user on command of {message.from_user.id}...")
    try:
        user_id = await client.get_users(user_ids=message.command[1])
        user_id = user_id.id
    except:
        await message.reply("❌ Invalid User!")
        return

    if user_id in root["banned"]:
        await message.reply("User is already banned!")
        return

    if user_id in root["users"]:
        root["users"].remove(user_id)

    database.ban_user(user_id=user_id)

    printlog(f"User {str(object=user_id)} has been banned!")
    await message.reply(f"✅ User {user_id} has been banned!")


@app.on_message(
    filters=filters.command(commands="unban", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def unban(client: pyrogram.Client, message: Message):
    printlog(f"Unbanning user on command of {message.from_user.id}...")
    try:
        user_id = await client.get_users(user_ids=message.command[1])
        user_id = user_id.id
    except:
        await message.reply("❌ Invalid User!")
        return

    if user_id not in root["banned"]:
        await message.reply("User is not present in banned list!")
        return

    database.unban_user(user_id=user_id)

    printlog(f"User {str(object=user_id)} has been unbanned!")
    await message.reply(f"✅ User {user_id} has been unbanned!")


@app.on_message(
    filters=filters.command(commands="setmilestone", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def setmilestone(_, message: Message):
    try:
        milestones_list = [int(x.strip()) for x in message.command[1].split(',')]
        varfile.milestones = milestones_list
        varfile.next_milestone_index = 0
        varfile.milestone_reached = False
        await message.reply(f"✅ Milestones set to: {milestones_list}\n\nFirst target: {milestones_list[0]} members")
        printlog(f"Milestones updated to {milestones_list}")
    except:
        await message.reply("❌ Invalid format!\n\nUse: /setmilestone 50,100,200,500,1000")


@app.on_message(
    filters=filters.command(commands="checkmilestone", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def checkmilestone(_, message: Message):
    current = len(root["users"])
    if not hasattr(varfile, 'milestones') or not varfile.milestones:
        await message.reply("❌ No milestones set! Use /setmilestone first.")
        return
    
    try:
        if varfile.next_milestone_index < len(varfile.milestones):
            next_milestone = varfile.milestones[varfile.next_milestone_index]
            needed = next_milestone - current
            await message.reply(
                f"📊 **Milestone Progress**\n\n"
                f"👥 Current members: {current}\n"
                f"🎯 Next milestone: {next_milestone}\n"
                f"📈 Need: {needed} more members!\n"
                f"🏁 All milestones: {varfile.milestones}"
            )
        else:
            await message.reply(
                f"🎉 **All Milestones Completed!** 🎉\n\n"
                f"👥 Final member count: {current}\n"
                f"🏁 Milestones: {varfile.milestones}\n\n"
                f"Use /resetmilestone to start over or /setmilestone to set new targets."
            )
    except Exception as e:
        await message.reply(f"Error checking milestone: {e}")


@app.on_message(
    filters=filters.command(commands="resetmilestone", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def resetmilestone(_, message: Message):
    varfile.next_milestone_index = 0
    varfile.milestone_reached = False
    if hasattr(varfile, 'milestones') and varfile.milestones:
        await message.reply(f"✅ Milestone tracking reset!\n\nNext target: {varfile.milestones[0]} members")
    else:
        await message.reply("✅ Milestone tracking reset! Use /setmilestone first to set targets.")
    printlog(f"Milestone tracking reset by {message.from_user.id}")


preliminaries()
print("=" * 50)
print("🎉 Bot Started Successfully! 🎉")
print("=" * 50)
if hasattr(varfile, 'milestones') and varfile.milestones:
    print(f"📊 Milestones configured: {varfile.milestones}")
else:
    print(f"📊 Milestones: Not set (use /setmilestone)")
print(f"👑 Admin ID: {varfile.admins}")
print(f"💬 Group ID: {group_id}")
print(f"📢 Channel ID: {channel_id}")
print("=" * 50)
print("Bot is running... Press Ctrl+C to stop")
print("=" * 50)
app.run()