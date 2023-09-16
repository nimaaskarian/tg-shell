async def get_replied_message(client,event):
    return (await client.get_messages(event.chat_id, ids=event.reply_to_msg_id))[0]

def user_full_name(user):
    if not user.first_name:
        return user.last_name

    if not user.last_name:
        return user.first_name

    return f"{user.first_name} {user.last_name}"

def tag_user(user):
    return f"[{user_full_name(user)}](tg://user?id={user.id})"

