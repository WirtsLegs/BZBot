server_id = <ID here>
bot_channel = 863088197135106115
mission_channels = []

admin_roles = [863057821166600202, 863115120468426803, 863084151380901889]

tentativeReact = "<:tentative:863657977377194014>"
declinedReact = "<:declined:863650407624212491>"
configReact = "<:edit:863785768156528640>"

event_auto_delete = 21600
event_reminder = 3600

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
                  "Please  enter a title for this mission, keep it short and to the point", 120, 0),
                 ("description", "Please provide a description",
                  "Describe your OP, what is the situation? mission? who are we? who are the enemy? etc", 300, 0),
                 ("map_selection", "Please select a map:", None, 60, 1, maps),
                 ("difficulty", "Please input a number from 0 - 10 for the difficulty", None, 60, 0),
                 ("modpack", "Is the BZ Modpack required?", "type yes for yes, anything else for no", 60, 2),
                 ("event_time", "Please input date and time with timezone", "Acceptable formats include:\nFriday at 9pm UTC\nTomorrow at 18:00 PST\nNow\nIn 1 hour CEST\nYYYY-MM-DD 7:00 PM EDT", 120, 3),
                 ("roles", "Select Airframes:", "Reply 'done' when all airframes selected", 60, 4, airframes)]

#kick config down here
#dont kick me brah
one_week = [867822587517206528, 863057821166600202, 863115120468426803, 863084151380901889, 863256789931655222]
one_month = [863057821166600202, 863115120468426803, 863084151380901889, 863256789931655222]
kick_reason="This is a placeholder kick message to test a purge feature, guys go ahead and rejoin with https://discord.gg/bu8TRfzYUx"