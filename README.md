# Gazzetta UNICT

[Live Demo](https://t.me/unictnews)  
[Live Demo DEV](https://t.me/gazzettaUNICTDev)

## Installation

### Docker

You can run this project locally using Docker by building the image and then running a container

#### Building the image

```
$ git clone https://github.com/UNICT-DMI/Gazzetta-UNICT.git
$ cd Gazzetta-UNICT
$ docker build --tag gazzetta-unict .
```

#### Add credentials

Create a duplicate file of `settings.yaml.dist` named `settings.yaml`:

```
$ cp data/settings.yaml.dist data/settings.yaml
```

Edit the values inside the configuration file for each site as you see fit, specifically:

```
token: ""       <string containing the bot's unique identifier>
chat_id: 123456 <chat_id of the channel in which the bot will post its messagges>
chat_id_dev:    <list of chat_ids with devs to receive technical exception regarding the bot>
  - 123456
  - 123456
  - ... 
```

_(If you don't have a token, message Telegram's [@BotFather](http://telegram.me/Botfather) to create a bot and get a token for it)_


#### Running the Container

Once you have correctly added all the necessary information you will be able to run the container by launching this command while inside the root folder:

```
$ docker run -it \
    --name bot \
    --mount type=bind,source="$(pwd)/data",destination=/app/data \
    gazzetta-unict
```
### Manually

If you want to test the bot by creating your personal instance, follow this steps:

Clone this repo with:

```
$ git clone https://github.com/UNICT-DMI/Gazzetta-UNICT.git
```


Install wkhtmltopdf using the right package for your distribution on their [download page](https://wkhtmltopdf.org/downloads.html)



Install project dependecies with:

```
$ pip3 install -r requirements.txt
```

Now is time to setup the bot's credentials, go to the [**Add credentials**](#add-credentials) section for more information, then come back here!

Run `python3 main.py` every X minutes to check


### Credits

- Luca Greco
