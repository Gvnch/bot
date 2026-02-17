@bot.message_handler(content_types=['photo', 'animation', 'video'])
def get_file_ids(m):
    if m.content_type == 'photo':
        # نأخذ آخر صورة لأنها تكون بأعلى دقة
        file_id = m.photo[-1].file_id
        bot.reply_to(m, f"🖼 **ID الصورة:**\n<code>{file_id}</code>", parse_mode="HTML")
    
    elif m.content_type == 'animation':
        file_id = m.animation.file_id
        bot.reply_to(m, f"🎬 **ID الصورة المتحركة (GIF):**\n<code>{file_id}</code>", parse_mode="HTML")

    elif m.content_type == 'video':
        file_id = m.video.file_id
        bot.reply_to(m, f"📹 **ID الفيديو:**\n<code>{file_id}</code>", parse_mode="HTML")
