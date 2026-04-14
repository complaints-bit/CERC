import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add translate text and safe limit helpers
helpers = """
# ── Translation Helper ──────────────────────────────────────────────────
TRANSLATION_CACHE = {}

def translate_text(text: str, target_lang_id: str) -> str:
    if target_lang_id == "lang_english" or not target_lang_id or not groq_client:
        return text
    
    cache_key = f"{target_lang_id}:{text}"
    if cache_key in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[cache_key]
        
    lang_map = {
        "lang_hindi": "Hindi",
        "lang_gujarati": "Gujarati",
        "lang_marathi": "Marathi"
    }
    target_lang = lang_map.get(target_lang_id, "English")
    if target_lang == "English":
        return text
        
    try:
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_lang}. Preserve all formatting, emojis. ONLY output the translation, nothing else, without quotes."},
                {"role": "user", "content": text}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        translated = completion.choices[0].message.content.strip()
        if translated.startswith('"') and translated.endswith('"'):
            translated = translated[1:-1]
        TRANSLATION_CACHE[cache_key] = translated
        return translated
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return text

def safe_truncate(text: str, length: int) -> str:
    if len(text) <= length:
        return text
    return text[:length-1] + "…"

# ── Language Selection ──────────────────────────────────────────────────"""

content = content.replace("# ── Language Selection ──────────────────────────────────────────────────", helpers)

# 2. Update send_category_menu
cat_menu_old = '''def send_category_menu(to: str):
    """
    Show available categories directly from the loaded JSON (Expect ~8).
    + options to describe issue.
    """
    rows = []
    for cat in CATEGORIES:
        clean = cat.replace(" ", "_").replace("&", "n")[:20]
        rows.append({
            "id": f"cat_{clean}",
            "title": cat[:24],
            "description": "Select this category"
        })

    option_rows = [
        {"id": "cat_describe", "title": "✍️ Describe Your Issue", "description": "Type your complaint for AI matching"},
    ]

    send_interactive_list(
        to,
        header="Select Category 📂",
        body="Choose a complaint category from the list, or describe your issue for smart matching:",
        footer="Select an option",
        button="Choose Category",
        sections=[
            {"title": "Categories", "rows": rows[:10]}, # Max 10 per section
            {"title": "More Options", "rows": option_rows},
        ]
    )'''

cat_menu_new = '''def send_category_menu(to: str, session: UserSession):
    """
    Show available categories directly from the loaded JSON (Expect ~8).
    + options to describe issue.
    """
    rows = []
    for cat in CATEGORIES:
        clean = cat.replace(" ", "_").replace("&", "n")[:20]
        cat_t = translate_text(cat, session.lang)
        rows.append({
            "id": f"cat_{clean}",
            "title": safe_truncate(cat_t, 24),
            "description": safe_truncate(translate_text("Select this category", session.lang), 72)
        })

    option_rows = [
        {
            "id": "cat_describe",
            "title": safe_truncate(translate_text("✍️ Describe Issue", session.lang), 24),
            "description": safe_truncate(translate_text("Type for AI matching", session.lang), 72)
        },
        {
            "id": "cat_change_lang",
            "title": safe_truncate(translate_text("🌍 Change Language", session.lang), 24),
            "description": safe_truncate(translate_text("Go back & change language", session.lang), 72)
        }
    ]

    header_t = safe_truncate(translate_text("Select Category 📂", session.lang), 60)
    body_t = safe_truncate(translate_text("Choose a complaint category from the list, or describe your issue for smart matching:", session.lang), 1024)
    footer_t = safe_truncate(translate_text("Select an option", session.lang), 60)
    button_t = safe_truncate(translate_text("Choose Category", session.lang), 20)

    send_interactive_list(
        to,
        header=header_t,
        body=body_t,
        footer=footer_t,
        button=button_t,
        sections=[
            {"title": safe_truncate(translate_text("Categories", session.lang), 24), "rows": rows[:10]},
            {"title": safe_truncate(translate_text("More Options", session.lang), 24), "rows": option_rows},
        ]
    )'''
content = content.replace(cat_menu_old, cat_menu_new)

# 3. Update send_predicted_categories
pred_old = '''def send_predicted_categories(to: str, predictions: list):
    """Show predicted categories as interactive list."""
    rows = []
    for cat in predictions:
        clean = cat.replace(" ", "_").replace("&", "n")[:20]
        rows.append({
            "id": f"cat_{clean}",
            "title": cat[:24],
            "description": "Select this category"
        })
    rows.append({
        "id": "cat_show_all",
        "title": "📋 Back to Categories",
        "description": "Browse the list of categories"
    })
    send_interactive_list(
        to,
        header="Category Match 🎯",
        body="Based on your description, here are the best matches:",
        footer="Select or browse all",
        button="Select Category",
        sections=[{"title": "Suggested", "rows": rows}]
    )'''

pred_new = '''def send_predicted_categories(to: str, predictions: list, session: UserSession):
    """Show predicted categories as interactive list."""
    rows = []
    for cat in predictions:
        clean = cat.replace(" ", "_").replace("&", "n")[:20]
        cat_t = translate_text(cat, session.lang)
        rows.append({
            "id": f"cat_{clean}",
            "title": safe_truncate(cat_t, 24),
            "description": safe_truncate(translate_text("Select this category", session.lang), 72)
        })
    rows.append({
        "id": "cat_show_all",
        "title": safe_truncate(translate_text("📋 Back to Categories", session.lang), 24),
        "description": safe_truncate(translate_text("Browse all categories", session.lang), 72)
    })
    send_interactive_list(
        to,
        header=safe_truncate(translate_text("Category Match 🎯", session.lang), 60),
        body=safe_truncate(translate_text("Based on your description, here are the best matches:", session.lang), 1024),
        footer=safe_truncate(translate_text("Select or browse all", session.lang), 60),
        button=safe_truncate(translate_text("Select Category", session.lang), 20),
        sections=[{"title": safe_truncate(translate_text("Suggested", session.lang), 24), "rows": rows}]
    )'''
content = content.replace(pred_old, pred_new)

# 4. Update send_faq_list
faq_old = '''def send_faq_list(to: str, category: str):
    """Send FAQ questions for a category as interactive list."""
    questions = get_questions_for_category(category)
    q_rows = []

    for i, q in enumerate(questions[:10]):   # max 10 per section
        q_rows.append({
            "id": f"faq_{i}",
            "title": q[:24],
            "description": q[:72]
        })

    opt_rows = [
        {
            "id": "faq_change_category",
            "title": "🔄 Start Over / Category",
            "description": "Go back to category selection"
        },
        {
            "id": "faq_file_complaint",
            "title": "📝 File a Complaint",
            "description": "My issue is different / I want to file"
        }
    ]

    send_interactive_list(
        to,
        header=f"{category[:50]} FAQ ❓",
        body="Here are common questions for this category.\\nSelect one for guidance, or choose an option below:",
        footer="Select an option",
        button="View Options",
        sections=[
            {"title": "Questions", "rows": q_rows},
            {"title": "Actions", "rows": opt_rows}
        ]
    )'''

faq_new = '''def send_faq_list(to: str, category: str, session: UserSession):
    """Send FAQ questions for a category as interactive list."""
    questions = get_questions_for_category(category)
    q_rows = []

    for i, q in enumerate(questions[:10]):   # max 10 per section
        q_trans = translate_text(q, session.lang)
        q_rows.append({
            "id": f"faq_{i}",
            "title": safe_truncate(q_trans, 24),
            "description": safe_truncate(q_trans, 72)
        })

    opt_rows = [
        {
            "id": "faq_change_category",
            "title": safe_truncate(translate_text("🔄 Start Over", session.lang), 24),
            "description": safe_truncate(translate_text("Change language/category", session.lang), 72)
        },
        {
            "id": "faq_file_complaint",
            "title": safe_truncate(translate_text("📝 File a Complaint", session.lang), 24),
            "description": safe_truncate(translate_text("My issue is different", session.lang), 72)
        }
    ]
    
    cat_trans = translate_text(category, session.lang)
    send_interactive_list(
        to,
        header=safe_truncate(f"{cat_trans[:50]} FAQ ❓", 60),
        body=safe_truncate(translate_text("Here are common questions for this category.\\nSelect one for guidance, or choose an option below:", session.lang), 1024),
        footer=safe_truncate(translate_text("Select an option", session.lang), 60),
        button=safe_truncate(translate_text("View Options", session.lang), 20),
        sections=[
            {"title": safe_truncate(translate_text("Questions", session.lang), 24), "rows": q_rows},
            {"title": safe_truncate(translate_text("Actions", session.lang), 24), "rows": opt_rows}
        ]
    )'''
content = content.replace(faq_old, faq_new)

# 5. Update send_collection_prompt
coll_old = '''def send_collection_prompt(to: str, state: str):
    """Send the data collection prompt for the current state."""
    prompt = COLLECTION_PROMPTS.get(state, "Please provide the details:")
    send_whatsapp_message(to, prompt)'''

coll_new = '''def send_collection_prompt(to: str, state: str, session: UserSession):
    """Send the data collection prompt for the current state."""
    prompt = COLLECTION_PROMPTS.get(state, "Please provide the details:")
    send_whatsapp_message(to, translate_text(prompt, session.lang))'''
content = content.replace(coll_old, coll_new)

# 6. Update send_summary
summ_old = '''def send_summary(to: str, session: UserSession):
    """Send complaint summary and confirm/edit buttons."""
    send_whatsapp_message(to, session.get_summary_text())
    send_interactive_buttons(to, "Please confirm or edit your complaint:", [
        ("action_confirm", "✅ Confirm"),
        ("action_edit", "✏️ Edit"),
    ])'''

summ_new = '''def send_summary(to: str, session: UserSession):
    """Send complaint summary and confirm/edit buttons."""
    send_whatsapp_message(to, translate_text(session.get_summary_text(), session.lang))
    send_interactive_buttons(to, translate_text("Please confirm or edit your complaint:", session.lang), [
        ("action_confirm", safe_truncate(translate_text("✅ Confirm", session.lang), 20)),
        ("action_edit", safe_truncate(translate_text("✏️ Edit", session.lang), 20)),
    ])'''
content = content.replace(summ_old, summ_new)

# 7. Update send_edit_field_list
edit_old = '''def send_edit_field_list(to: str, session: UserSession):
    """Send list of editable fields."""
    fields = session.get_editable_fields()
    rows = [{"id": fid, "title": name[:24], "description": "Edit this field"} for fid, name in fields]
    send_interactive_list(
        to,
        header="Edit Field ✏️",
        body="Which field would you like to edit?",
        footer="Select a field",
        button="Choose Field",
        sections=[{"title": "Fields", "rows": rows}]
    )'''

edit_new = '''def send_edit_field_list(to: str, session: UserSession):
    """Send list of editable fields."""
    fields = session.get_editable_fields()
    rows = []
    for fid, name in fields:
        name_t = translate_text(name, session.lang)
        rows.append({"id": fid, "title": safe_truncate(name_t, 24), "description": safe_truncate(translate_text("Edit this field", session.lang), 72)})
    send_interactive_list(
        to,
        header=safe_truncate(translate_text("Edit Field ✏️", session.lang), 60),
        body=safe_truncate(translate_text("Which field would you like to edit?", session.lang), 1024),
        footer=safe_truncate(translate_text("Select a field", session.lang), 60),
        button=safe_truncate(translate_text("Choose Field", session.lang), 20),
        sections=[{"title": safe_truncate(translate_text("Fields", session.lang), 24), "rows": rows}]
    )'''
content = content.replace(edit_old, edit_new)

# 8. Update handle_text
content = content.replace("send_predicted_categories(sender, predictions)", "send_predicted_categories(sender, predictions, session)")
content = content.replace("send_whatsapp_message(sender, \"🔍 Analyzing your complaint...\")", "send_whatsapp_message(sender, translate_text(\"🔍 Analyzing your complaint...\", session.lang))")
content = content.replace("send_collection_prompt(sender, COLLECT_OPPOSITE_NAME)", "send_collection_prompt(sender, COLLECT_OPPOSITE_NAME, session)")
content = content.replace("send_collection_prompt(sender, COLLECT_OPPOSITE_ADDRESS)", "send_collection_prompt(sender, COLLECT_OPPOSITE_ADDRESS, session)")
content = content.replace("send_collection_prompt(sender, COLLECT_OPPOSITE_PHONE)", "send_collection_prompt(sender, COLLECT_OPPOSITE_PHONE, session)")
content = content.replace("send_collection_prompt(sender, COLLECT_OPPOSITE_EMAIL)", "send_collection_prompt(sender, COLLECT_OPPOSITE_EMAIL, session)")
content = content.replace("send_collection_prompt(sender, COLLECT_MONETARY)", "send_collection_prompt(sender, COLLECT_MONETARY, session)")
content = content.replace("send_collection_prompt(sender, COLLECT_DOCS)", "send_collection_prompt(sender, COLLECT_DOCS, session)")
content = content.replace("send_whatsapp_message(sender, \"📎 Please upload a photo/document, or type *done* to proceed.\")", "send_whatsapp_message(sender, translate_text(\"📎 Please upload a photo/document, or type *done* to proceed.\", session.lang))")
content = content.replace("send_whatsapp_message(sender, \"✅ Updated!\")", "send_whatsapp_message(sender, translate_text(\"✅ Updated!\", session.lang))")
content = content.replace("send_collection_prompt(sender, COLLECT_DESCRIPTION)", "send_collection_prompt(sender, COLLECT_DESCRIPTION, session)")
content = content.replace("send_whatsapp_message(sender, \"Something went wrong. Type *hi* to restart.\")", "send_whatsapp_message(sender, translate_text(\"Something went wrong. Type *hi* to restart.\", session.lang))")

# 9. Update handle_interactive
content = content.replace("send_whatsapp_message(sender, confirmation)", "send_whatsapp_message(sender, translate_text(confirmation, session.lang))")
content = content.replace("send_category_menu(sender)", "send_category_menu(sender, session)")
content = content.replace("send_whatsapp_message(sender, \"✍️ Please describe your issue in a few words:\")", "send_whatsapp_message(sender, translate_text(\"✍️ Please describe your issue in a few words:\", session.lang))")
# Inside cat_ routing:
content = content.replace("send_whatsapp_message(sender, f\"📂 Category: *{category}*\")", "send_whatsapp_message(sender, translate_text(f\"📂 Category: *{category}*\", session.lang))")
content = content.replace("send_whatsapp_message(sender, f\"Category selected: *{selected_title}*\")", "send_whatsapp_message(sender, translate_text(f\"Category selected: *{selected_title}*\", session.lang))")
content = content.replace("send_faq_list(sender, category)", "send_faq_list(sender, category, session)")
content = content.replace("send_faq_list(sender, selected_title)", "send_faq_list(sender, selected_title, session)")

# faq_change_category routing:
old_faq_change = '''    if selected_id == "faq_change_category":
        session.state = CATEGORY_MENU
        session.category = None
        session.selected_question = None
        send_category_menu(sender)
        return'''
new_faq_change = '''    if selected_id == "faq_change_category":
        reset_session(sender)
        send_language_selection(sender)
        return
        
    if selected_id == "cat_change_lang":
        reset_session(sender)
        send_language_selection(sender)
        return'''
content = content.replace(old_faq_change, new_faq_change)

# Descriptions logic updates
old_desc = "send_whatsapp_message(sender, f\"📝 We have your description:\\n_{session.complaint_description}_\\n\\nLet's collect more details.\")"
new_desc = "send_whatsapp_message(sender, translate_text(f\"📝 We have your description:\\n_{session.complaint_description}_\\n\\nLet's collect more details.\", session.lang))"
content = content.replace(old_desc, new_desc)

# FAQ response:
ans_old = '''            answer = get_dummy_answer(session.category, question)
            send_whatsapp_message(sender, answer)
            session.state = FAQ_ANSWER
            send_interactive_buttons(sender, "Was this helpful?", [
                ("ans_satisfied", "✅ Satisfied"),
                ("ans_file", "📝 File Complaint"),
                ("ans_back", "🔙 Back"),
            ])'''
ans_new = '''            answer = get_dummy_answer(session.category, question)
            send_whatsapp_message(sender, translate_text(answer, session.lang))
            session.state = FAQ_ANSWER
            send_interactive_buttons(sender, translate_text("Was this helpful?", session.lang), [
                ("ans_satisfied", safe_truncate(translate_text("✅ Satisfied", session.lang), 20)),
                ("ans_file", safe_truncate(translate_text("📝 File Complaint", session.lang), 20)),
                ("ans_back", safe_truncate(translate_text("🔙 Back", session.lang), 20)),
            ])'''
content = content.replace(ans_old, ans_new)

# Satisfaction message
content = content.replace("send_whatsapp_message(sender, \"🙏 Glad we could help! Type *hi* to start a new query.\")", "send_whatsapp_message(sender, translate_text(\"🙏 Glad we could help! Type *hi* to start a new query.\", session.lang))")

# Confirm summary
confirm_old = '''        send_whatsapp_message(
            sender,
            f"🎉 *Complaint Filed Successfully!*\\n\\n"
            f"🎫 Your Ticket ID: *{ticket_id}*\\n\\n"
            f"We will review your complaint and get back to you.\\n"
            f"📞 Consumer Helpline: 1800-11-4000\\n\\n"
            f"Thank you for using CERC Support! 🙏"
        )'''
confirm_new = '''        msg = (
            f"🎉 *Complaint Filed Successfully!*\\n\\n"
            f"🎫 Your Ticket ID: *{ticket_id}*\\n\\n"
            f"We will review your complaint and get back to you.\\n"
            f"📞 Consumer Helpline: 1800-11-4000\\n\\n"
            f"Thank you for using CERC Support! 🙏"
        )
        send_whatsapp_message(sender, translate_text(msg, session.lang))'''
content = content.replace(confirm_old, confirm_new)

# Edit field prompts
edit_prompt_old = '''        prompt = field_prompts.get(selected_id, "Enter the new value:")
        send_whatsapp_message(sender, prompt)'''
edit_prompt_new = '''        prompt = field_prompts.get(selected_id, "Enter the new value:")
        send_whatsapp_message(sender, translate_text(prompt, session.lang))'''
content = content.replace(edit_prompt_old, edit_prompt_new)

# 10. Update handle_media
med_old_1 = '''    if session.state != COLLECT_DOCS:
        send_whatsapp_message(
            sender,
            "📎 We're not collecting documents right now. "
            "Please follow the current step or type *hi* to restart."
        )'''
med_new_1 = '''    if session.state != COLLECT_DOCS:
        send_whatsapp_message(
            sender,
            translate_text("📎 We're not collecting documents right now. Please follow the current step or type *hi* to restart.", session.lang)
        )'''
content = content.replace(med_old_1, med_new_1)

med_old_2 = '''        send_whatsapp_message(
            sender,
            f"✅ Document received! ({count} total)\\n"
            f"Send more, or type *done* to proceed."
        )'''
med_new_2 = '''        send_whatsapp_message(
            sender,
            translate_text(f"✅ Document received! ({count} total)\\nSend more, or type *done* to proceed.", session.lang)
        )'''
content = content.replace(med_old_2, med_new_2)

med_old_3 = '''        send_whatsapp_message(sender, "⚠️ Could not process the file. Please try again.")'''
med_new_3 = '''        send_whatsapp_message(sender, translate_text("⚠️ Could not process the file. Please try again.", session.lang))'''
content = content.replace(med_old_3, med_new_3)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Finished rewriting app.py!")
