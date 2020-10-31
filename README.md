# lance-a-bot-docker


Docker container to host "Lance-a-bot," a Discord bot that creates channels for Pokémon events by pulling information from the Pokemon Event Locator. It can also add the event to a shared Google Calendar. Currently requires a login to pokemon.com and a Google API key. 

The Google Auth API Credentials (?) file must be placed in "/config/". When setting up the Docker container, a pokemon.com login and password must be provided to be stored as environment variables. The GOES_TOKEN is currently unused, but may be used in the future for event travel time from a location. Google Maps may also be able to provide this functionality. 

Some assembly still required. Will need to setup where the bot posts events, the Google Calendar it posts to, and the message for the meetup (if desired). 

# Docker command

    docker pull ckohnke/lance-a-bot

# Bot Commands

| Syntax      | Description |
| ----------- | ----------- |
| $hello      | Hello World       |
| $info   | prints bot commands and syntax (needs updating)        |
| $tid ##-##-###### [time] [cal] [lookup]   | the main command. Used to lookup info about a tournament from the Event Locator.        |
| [time]   | Adds a meetup time in the event description posted ot the channel.         |
| [cal]   | If true, adds the event to the Google Calendar        |
| [lookup]   | Does not create a channel and simply prints out the event information.        |

# Examples

    $tid 01-11-000101 7:30PM true

Looks up event 01-11-000101, creates a channel to discuss the event, sets the carpool time to 7:30PM, and adds the event to the Google Calendar. 

    $tid 01-11-000101 lookup

Looks up and posts information about event 01-11-000101.

# TODO

* Generalize for a regular Discord Bot?
    * Role permissions to call certain commands
    * Way to securely store login to PCOM, unless the Event Locator allows non-members to view it now.
        * No, as of 10/20/2020
    * Setup bot channel to post events
        * Allow for separate TCG and VG channels (and prereleases?)
    * Make calendar optional / Allow user to select calendar. 
    * Make carpool option optional.
* ~~Auto-delete channel(s) once an event is marked as complete (tournament uploaded by the TO) + arbitrary time~~
    * Doesn't happen automagically. Might need to generalize more before can run automatically.
* Non PCOM events (Battlefy / Challonge)
    * Battlefy doesn't appear to have an API to tap into and it's horrible to scrape. 
    * Challonge might be "better," but marginally. 
* Does anything change with the new PEM announcement?
