server_id = 863056195950870548
bot_channel = 863088197135106115
mission_channels = [863056275759038494]

admin_roles = [863057821166600202, 863115120468426803, 863084151380901889]

tentativeReact = "<:tentative:863657977377194014>"
declinedReact = "<:declined:863650407624212491>"
editReact = "<:edit:863785768156528640>"
deleteReact = "<:delete:863786011317370890>"
configReact = "<:edit:863785768156528640>"

event_auto_delete = 21600

maps = ["Caucasas", "Marianas", "Persian Gulf", "Syria", "Normandy", "Channel"]

airframes = {
    "F/A-18C": "<:FA18Hornet:863582543349547019>",
    "F-14": "<:F14BTomcat:863582475334189056>",
    "AV8B": "<:AV8BHarrier:863582446656946197>",
    "Gazelle": "<:sa342:863582436674502678>",
    "Huey": "<:UH1HHuey:863582424016486411>",
    "JF-17": "<:JF17:863582409089089597>",

}

question_list = [("title", "What is the title of your mission?",
                  "Please  enter a title for this mission, keep it short and to the point", 60, 0),
                 ("description", "Please provide a description",
                  "Describe your OP, what is the situation? mission? who are we? who are the enemy? etc", 120, 0),
                 ("map_selection", "Please select a map:", None, 30, 1, maps),
                 ("difficulty", "Please input a number from 0 - 10 for the difficulty", None, 30, 0),
                 ("modpack", "Is the BZ Modpack required?", "type yes for yes, anything else for no", 30, 2),
                 ("event_time", "Please input date and time with timezone", "Acceptable formats include:\nFriday at 9pm UTC\nTomorrow at 18:00 PST\nNow\nIn 1 hour CEST\nYYYY-MM-DD 7:00 PM EDT", 60, 3),
                 ("airframes", "Select Airframes:", "Reply 'done' when all airframes selected", 30, 4, airframes)]
