
bot_channel = 863088197135106115
mission_channels = [863056275759038494]

tentativeReact = "tentative"
declinedReact = "declined"
editReact = "edit"
deleteReact = "delete"
summaryReact = "summary"

maps = ["Caucasas", "Marianas", "Persian Gulf", "Syria", "Normandy", "Channel"]

airframes = {
    "F/A-18C": "FA18Hornet"
}

question_list = [("title", "What is the title of your mission?",
                  "Please  enter a title for this mission, keep it short and to the point", 60, 0),
                 ("description", "Please provide a description",
                  "Describe your OP, what is the situation? mission? who are we? who are the enemy? etc", 120, 0),
                 ("map_selection", "Please select a map:", None, 30, 1, maps),
                 ("difficulty", "Please input a number from 0 - 10 for the difficulty", None, 30, 0),
                 ("modpack", "Is the BZ Modpack required?", "type yes for yes, anything else for no", 30, 2),
                 ("event_time", "Please input date and time with timezone", "Acceptable formats include:\nFriday at 9pm UTC\nTomorrow at 18:00 PST\nNow\nIn 1 hour CEST\nYYYY-MM-DD 7:00 PM EDT", 60, 3)]