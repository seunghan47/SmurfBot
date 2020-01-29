# GroupMe_Bot
This is a bot I'm working on a small groupme group I'm in. This is something I'll work on in my spare time. Nothing but 
just a fun little side project for when I'm bored.

## Libraries used
[Groupy: an API wrapper for Groupme](https://github.com/rhgrant10/Groupy)

[Documentation for Groupy](http://groupy.readthedocs.io/en/master/index.html)

## Instructions
There are multiple ways to run the bot.

1. python3 bot_start.py
2. scripts/bot.sh start|stop|restart (This one will run it as a background process)
3. Docker

Make sure to change the information in main.py to what you want such as the location of your groupme key or youtube key.

You have to pick a deliminator to use this bot. The default one is `$`. You can change it by passing it to the bot 
object

## Credentials
The bot looks for Credentials in two places. It will look for the environmental variable first.

1. Environmental Variables: Looks for the environmental variable `GROUPME_KEY` and uses that value
2. creds/groupme.key: a text file with the token in the first line


## Docker
Using the provided Dockerfile, you can build an image with `docker build -t groupme-bot`.

If you don't mount a volume to the container, any tags that are made will be lost once the container is stopped.

If you don't mount a volume that contains `groupme.key` to `/app/creds`, you need to pass it in as an environmental variable

Once the image is built, you can run it with:

`docker run -ditv --rm -v [local tag folder]:/app/tags -v [local creds folder]:/app/creds --name groupme groupme-bot`

add `-e GROUPME_KEY=[token]` if you need the token as an environmental variable

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


### Tag System

| command | argument(s) | example
| ------------- |:-------------:| -------------------------------------------------:|
| create        | [tag_name] [stuff]**      | tag create cooltag this is a cool tag |
| edit          | [tag_name] [stuff]**      | tag edit cooltag this is a new edit   |
| delete        | [tag_name]                | tag delete cooltag                    |
| none          | [tag_name]                | tag cooltag                           |
| list          | none                      | tag list                              |
| owner         | [tag_name]                | tag owner cooltag                     |
| gift          | [tag_name] @mention       | tag cooltag @new_owner                |
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
  "tag_name": {
    "content": "some string, link to website/image/video/et, or groupme image/video url",
    "owner": "owner_id_number"
  },
    "tag_name2": {
    "content": "some string, link to website/image/video/et, or groupme image/video url",
    "owner": "owner_id_number"
  },
  ...
}
```
