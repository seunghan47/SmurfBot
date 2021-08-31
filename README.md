# SmurfBot
This is a bot I'm working on for a small discord group I'm in. This is something I'll work on in my spare time.
This was originally for a groupme chat, but we transitioned to discord.
Nothing but just a fun little side project for when I'm bored.

## Libraries used
[Discord.py](https://discordpy.readthedocs.io/en/stable/#)

[python-atomicwrites: Powerful Python library for atomic file writes](https://github.com/untitaker/python-atomicwrites)

[google-api-python-client](https://developers.google.com/youtube/v3/quickstart/python) (only needed if you will be doing yt searches from the bot)


## Instructions
Before the bot can listen to a group, it needs to be added to that group. Do that first or the bot won't work.

There are two ways to run the bot.

1. python3 start.py
2. Docker

Make sure to change the information in main.py to what you want such as the location of your groupme key or youtube key.

You have to pick a deliminator to use this bot. The default one is `$`. You can change it by passing it to the bot 
object

## Config and Credentials
The bot looks for Credentials in `config.ini` that is at the root of the repo. An example file has been provided.


## Docker
Using the provided Dockerfile, you can build an image with `docker build -t groupme-bot .`

If you don't mount a volume to the container, any tags that are made will be lost once the container is stopped.

Once the image is built, you can run it with:

`docker run -ditv --rm -v [local tag folder]:/home/groupme/app/tags -v [local config.ini]:/home/groupme/app/config.ini --name groupme groupme-bot`


add `-m [amount]` or `--cpus=[number]` to limit the ram or CPU cores the container can use

To attach to a detached container, follow these steps (assuming you ran it with the -it arguments):

`docker ps` to find the Container ID

`docker attach [Container ID]` to attach to it

`docker stop [Container ID]` to stop the container

`Ctrl-C` to shutdown the container

`Ctrl-p Ctrl-q` to detach from it

## Commands
#### Everything command should lead with the delimiter (the default delimiter is "$")

| command | argument(s) | example
| ------------- |:-------------:| --------------------------------------:|
| avatar        | [mention_name]         | avatar @name                  |
| git           | none                   | git                           |
| yt**          | [query]                | yt skateboard tricks

** yt command will only post the first link from the youtube search

### Tag System

| command | argument(s) | example
| ------------- |:-------------:| -------------------------------------------------:|
| create        | [tag_name] [stuff]**      | tag create cooltag this is a cool tag |
| edit          | [tag_name] [stuff]**      | tag edit cooltag this is a new edit   |
| delete        | [tag_name]                | tag delete cooltag                    |
| none          | [tag_name]                | tag cooltag                           |
| list          | none                      | tag list                              |
| owner         | [tag_name]                | tag owner cooltag                     |
| gift          | [tag_name] @mention       | tag gift cooltag @new_owner           |
| rename        | [tag_name] [new tag_name] | tag rename cooltag coolertag          |
| help          | none                      | tag help                              |

** [stuff] can be a string, a link to anything, or an image that is upload through groupme

** If [stuff] is an image uploaded through groupme, then the description with the image should just be:
 
 `tag create [tag_name]`
 
 The commands `create`, `edit`, `delete`, `gift`, and `rename` can only be down by the owner of the tag. 
 The owner is whoever created the tag.
 
 `owner` command will get the user_id of the owner and will find attempt to match it to the nickname of the owner.
 
 
 #### JSON structure
 
 This is the json structure of tags
 
 ```json
{
  "id": "group id goes here",
  "name": "group name goes here",
  "tags": {
    "tag1": {
      "content": "tag1 content",
      "owner": "owner id"
    },
    "tag2": {
      "content": "tag2 content",
      "owner": "owner id"
    }
  }
}
```
