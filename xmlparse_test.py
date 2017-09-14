from xml.etree.ElementTree import parse

# TODO: Put parsing into separate functions
# TODO: Parse into dictionaries
# load xml tv file and get root object
tree = parse('xmltv.xml')
root = tree.getroot()

# parse channel list and print it to console
print("Channels", end="\n")
for channel in root.findall("channel"):
    display_name = channel.find("display-name").text
    lang = channel.find("display-name").get("lang")
    channel_id = channel.get("id")
    icon = ""
    if channel.find("icon") is not None:
        icon = channel.find("icon").get("src")
    print(display_name, lang, channel_id, icon, sep=" ", end="\n")

# TODO: May be more than one category
# TODO: May be titles in different languages
# TODO: Add description
# TODO: Add credits
# TODO: Parse start and end time
# parse programme and print it to console
print("", "", "", "", "Programme", sep="\n", end="\n")
for programme in root.findall("programme"):
    start = programme.get("start")
    stop = programme.get("stop")
    channel_id = programme.get("channel")
    title = programme.find("title").text
    title_lang = programme.find("title").get("lang")
    category = ""
    category_lang = ""
    if programme.find("category") is not None:
        category = programme.find("category").text
        category_lang = programme.find("category").get("lang")
    print(title, title_lang, category, category_lang, sep=" ", end="\n")
