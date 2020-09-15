import praw
from pprint import pprint

DONT_COPY_POST_FLAIR = ("Draft")

reddit = None
source_sub = None
target_sub = None
target_sub_title = None
first_run: bool = True
source_sub_name = None


def main():
    global target_sub_title, source_sub_name

    source_sub_name = input("Input source sub name: ")
    target_sub_name = input("Input target sub name: ")

    do_startup_checks(source_sub_name, target_sub_name)

    while True:
        selection = print_menu()
        handle_menu_selection(selection)


def do_startup_checks(source_sub_name: str, target_sub_name: str):
    global reddit, source_sub, target_sub, target_sub_title

    reddit = praw.Reddit("main")
    print("User authorized:", reddit.user.me())

    source_sub = reddit.subreddit(source_sub_name)

    moderated_lowercase = [x.display_name.lower()
                           for x in reddit.user.me().moderated()]
    if source_sub_name.lower() not in moderated_lowercase:
        raise Exception(f"Not a mod of {source_sub_name}")

    if target_sub_name.lower() not in moderated_lowercase:
        raise Exception(f"Not a mod of {target_sub_name}")

    target_sub = reddit.subreddit(target_sub_name)
    # Make it load the attributes
    target_sub_title = target_sub.title
    print(
        f"Processing: {target_sub.display_name} ({target_sub_title})...")


def print_menu() -> int:
    global first_run

    if first_run:
        first_run = False
    else:
        reload_subs()

    print()
    print()
    print("Actions:")
    print("-------------------------------")
    print("1 ) Copy Rules")
    print("2 ) Copy Removal Reasons")
    print("3 ) Copy Post Flair")
    print("4 ) Copy AutoModerator Rules")
    print("5 ) Copy Welcome Message Settings")
    print("6 ) Copy Rules Wiki")
    print("7 ) Copy Taskerbot Wiki")
    print("8 ) Copy Index Wiki (from wiki template)")
    print("9 ) Copy Description (from wiki template)")
    print("10) Copy Old Reddit Sidebar (from wiki template)")
    print("11) Copy Subreddit Settings (spoiler tags, etc)")
    print("---")
    print("99) Perform all actions above")
    print("q ) Quit (or just press enter to quit)")
    print()
    selection = input("Please make a selection: ")
    if not selection or selection == "q":
        exit(0)
    return int(selection)


def handle_menu_selection(selection):
    menu = {
        1: copy_rules,
        2: copy_removal_reasons,
        3: copy_post_flair,
        4: copy_automoderator_rules,
        5: copy_welcome_message_settings,
        6: copy_rules_wiki,
        7: copy_taskerbot_wiki,
        8: copy_index_wiki,
        9: copy_description,
        10: copy_old_reddit_sidebar,
        11: copy_subreddit_settings,
        99: perform_all_actions,
    }

    f = menu.get(selection, lambda: print("Invalid selection."))
    f()


def copy_rules():
    print_step("Copying rules...")

    for rule in source_sub.rules:
        short_name = t(rule.short_name)
        kind = t(rule.kind)
        description = t(rule.description)
        violation_reason = t(rule.violation_reason)

        if short_name not in target_sub.rules:
            print(f"Adding rule: {short_name}")
            target_sub.rules.mod.add(
                short_name=short_name,
                kind=kind,
                description=description,
                violation_reason=violation_reason)
        else:
            existing_rule = target_sub.rules[short_name]
            print(f"Updating rule: {short_name}")
            existing_rule.mod.update(
                short_name=short_name,
                kind=kind,
                description=description,
                violation_reason=violation_reason)


def copy_removal_reasons():
    print_step("Copying removal reasons...")

    target_titles = {}
    for x in target_sub.mod.removal_reasons:
        target_titles[t(x.title)] = x.id

    for reason in source_sub.mod.removal_reasons:
        title = t(reason.title)
        message = t(reason.message)

        if title not in target_titles:
            print(f"Adding removal reason: {title}")
            target_sub.mod.removal_reasons.add(
                title=title,
                message=message)
        else:
            existing_removal_reason = target_sub.mod.removal_reasons[target_titles[title]]
            print(f"Updating removal reason: {title}")
            existing_removal_reason.update(
                title=title,
                message=message)


def copy_post_flair():
    print_step("Copying post flair...")

    target_titles = {}
    for x in target_sub.flair.link_templates:
        target_titles[x["text"]] = x["id"]

    for flair in source_sub.flair.link_templates:
        text = flair["text"]

        if text in DONT_COPY_POST_FLAIR:
            continue

        if text not in target_titles:
            print(f"Adding post flair: {text}")
            target_sub.flair.link_templates.add(
                text=flair["text"],
                css_class=flair["css_class"],
                text_editable=flair["text_editable"],
                background_color=flair["background_color"],
                text_color=flair["text_color"],
                mod_only=flair["mod_only"],
                allowable_content=flair["allowable_content"],
                max_emojis=flair["max_emojis"])
        else:
            template_id = target_titles[text]
            print(f"Updating post flair: {text}")
            target_sub.flair.link_templates.update(
                template_id,
                text=flair["text"],
                css_class=flair["css_class"],
                text_editable=flair["text_editable"],
                background_color=flair["background_color"],
                text_color=flair["text_color"],
                mod_only=flair["mod_only"],
                allowable_content=flair["allowable_content"],
                max_emojis=flair["max_emojis"])


def copy_wiki_page(src: str, dst: str = None, do_replacement: bool = True, remove_line: str = None):
    src_wiki = source_sub.wiki[src]
    src_wiki_settings = src_wiki.mod.settings()
    if not dst:
        dst = src

    content = src_wiki.content_md
    if do_replacement:
        content = t(content)

    if remove_line:
        content = content.replace(remove_line, "")

    reason = f"Copying settings from r/{source_sub_name}"

    dst_wiki_pages = [x.name for x in target_sub.wiki]
    dst_wiki = None

    if dst not in dst_wiki_pages:
        dst_wiki = target_sub.wiki.create(
            dst, content, reason=reason)
    else:
        dst_wiki = target_sub.wiki[dst]
        dst_wiki.edit(content, reason=reason)

    dst_wiki.mod.update(
        src_wiki_settings["listed"], src_wiki_settings["permlevel"])


def copy_automoderator_rules():
    print_step("Copying AutoModerator rules wiki...")

    copy_wiki_page("config/automoderator",
                   remove_line="moderators_exempt: false")


def copy_welcome_message_settings():
    print_step("Copying welcome message settings...")

    current_settings = source_sub.mod.settings()
    enabled = current_settings["welcome_message_enabled"]
    content = t(current_settings["welcome_message_text"])

    target_sub.mod.update(welcome_message_enabled=enabled,
                          welcome_message_text=content)


def copy_rules_wiki():
    print_step("Copying rules wiki...")

    copy_wiki_page("rules")


def copy_taskerbot_wiki():
    print_step("Copying taskerbot wiki...")

    copy_wiki_page("taskerbot", do_replacement=False)


def copy_index_wiki():
    print_step("Copying wiki index page...")

    copy_wiki_page("index_template", "index")


def copy_description():
    print_step("Copying description from template...")

    content = t(source_sub.wiki["description_template"].content_md)

    target_sub.mod.update(public_description=content)


def copy_old_reddit_sidebar():
    print_step("Copying old Reddit sidebar from template...")

    dst_wiki_pages = [x.name for x in target_sub.wiki]
    if "config/sidebar" not in dst_wiki_pages:
        print("\r\nYou must create a sidebar first. Then I can overwrite it.\r\n")
        return

    copy_wiki_page("sidebar_template", "config/sidebar")


def copy_subreddit_settings():
    print_step("Copying subreddit settings...")

    source_sub_settings = source_sub.mod.settings()

    spoilers_enabled = source_sub_settings["spoilers_enabled"]
    allow_videos = source_sub_settings["allow_videos"]

    target_sub.mod.update(spoilers_enabled=spoilers_enabled,
                          allow_videos=allow_videos)


def perform_all_actions():
    copy_rules()
    copy_removal_reasons()
    copy_post_flair()
    copy_automoderator_rules()
    copy_welcome_message_settings()
    copy_rules_wiki()
    copy_taskerbot_wiki()
    copy_description()
    copy_old_reddit_sidebar()
    copy_subreddit_settings()


def t(input_str: str) -> str:
    return input_str.replace("{subreddit}", target_sub.display_name).replace("{title}", target_sub_title)


def reload_subs():
    global source_sub, target_sub
    source_sub = reddit.subreddit(source_sub.display_name)
    target_sub = reddit.subreddit(target_sub.display_name)


def print_step(step_name: str):
    print()
    print()
    print(step_name)
    print()


if __name__ == "__main__":
    main()
