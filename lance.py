#!/usr/bin/env python3


# Work with Python 3.6
from __future__ import print_function
import discord
from discord.ext import commands
import requests
import re
from bs4 import BeautifulSoup
import datetime
import pytz
from tzwhere import tzwhere
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

#config = np.loadtxt("config",dtype=str)
#print(type(str(config[0])))

TOKEN = os.environ['GEOS_TOKEN']
USERNAME = os.environ['POP_UNAME']
PASSWORD = os.environ['POP_PASSWORD']

PWD = "/config/"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

print(discord.__version__)
print(TOKEN)
print(USERNAME)
print(PASSWORD)

LOGIN_URL = "https://sso.pokemon.com/sso/login?locale=en&service=https://club.pokemon.com/us/pokemon-trainer-club/caslogin"
URL = "https://www.pokemon.com/us/play-pokemon/pokemon-events/"

bot = commands.Bot(command_prefix='$')

# Google calendar integration
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists(PWD+'token.pickle'):
    with open(PWD+'token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            PWD+'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(PWD+'token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

def proc_fields(f,par):
    if(f.startswith('Tournament Name')):
        par['name']=f[len('Tournament Name'):]
    elif(f.startswith('Tournament ID')):
        par['idn']=f[len('Tournament ID'):]
    elif(f.startswith('Category')):
        par['category']=f[len('Category'):]
    elif(f.startswith('Date')):
        par['date']=f[len('Date'):]
    elif(f.startswith('Online Registration')):
        par['onlinereg']=f[len('Online Registration'):-2] # Click Here
        par['onlinereg']="YES - SEE POKEMON EVENT PAGE"
    elif(f.startswith('Registration')):
        par['registration']=f[len('Registration'):]
    elif(f.startswith('Product')):
        par['product']=f[len('Product'):]
    elif(f.startswith('Premier Event')):
        par['premier']=f[len('Premier Event'):].strip('\n ')
    elif(f.startswith('Status')):
        par['status']=f[len('Status'):]
    elif(f.startswith('Organizer Name')):
        par['to']=f[len('Organizer Name'):]
    elif(f.startswith('Venue Name')):
        par['venue']=f[len('Venue Name'):]
    elif(f.startswith('Address Line 1')):
        par['address1']=f[len('Address Line 1'):]
    elif(f.startswith('Address Line 2')):
        par['address2']=f[len('Address Line 2'):]
    elif(f.startswith('City')):
        par['city']=f[len('City'):]
    elif(f.startswith('Province/State')):
        par['state']=f[len('Province/State'):]
    elif(f.startswith('Postal/Zip Code')):
        par['zipcode']=f[len('Postal/Zip Code'):]
    elif(f.startswith('Country')):
        par['country']=f[len('Country'):]
    elif(f.startswith('\nWebsite\n')):
        par['website']=f[len('\nWebsite\n'):-1]
    elif(f.startswith('Admission')):
        par['cost']=f[len('Admission'):]
    elif(f.startswith('Junior Division Admission')):
        par['jrcost']=f[len('Junior Division Admission'):]
    elif(f.startswith('Senior Division Admission')):
        par['srcost']=f[len('Senior Division Admission'):]
    elif(f.startswith('Masters Division Admission')):
        par['macost']=f[len('Masters Division Admission'):]
    elif(f.startswith('Admission')):
        par['cost']=f[len('Admission'):len('Admission')+5]
    elif(f.startswith('Details')):
        par['details']=f[len('Details'):]
    elif(f.startswith('League Cup')):
        par['sanctioned']='League Cup - ' + f[len('League Cup'):]
    elif(f.startswith('League Challenge')):
        par['sanctioned']='League Challenge - ' + f[len('League Challenge'):]

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------ END')

@bot.command()
async def hello(ctx):
    print('------ START')
    print("hello()")

    msg = r"Hello %s"%(ctx.message.author.mention)
    await ctx.send(msg)

    print('------ END')

@bot.command()
async def info(ctx):
    print("------ START")
    print("info()")
    embed = discord.Embed(title="Lance-A-Bot", description="Bot to aid in tournament organizing")
    embed.add_field(name="$tid [tournament ID] [options]", value="Grabs the information of the given tournament id number and starts a carpool channel for that event.")
    embed.add_field(name="$tid [tournament ID] lookup", value="Grabs the information of the given tournament id numberumber and posts its information.")
    embed.add_field(name="$info", value="prints this message")
    embed.add_field(name="$hello", value="says hello!")


    await ctx.send(embed=embed)
    print("------ END")

@bot.command()
async def tid(ctx,tid : str,time = None, cal = None):
    print('------ START')
    print('tid()')

    permission = False
    for r in ctx.author.roles:
        if r.name == 'Shadow Government':
            permission = True
            break
        if r.name == 'Moderators':
            permission = True
            break

    if(not permission):
        await ctx.send("{} You do not have permission to use this command.".format(ctx.author.mention))
        print('------ END')
        return

    session_requests = requests.session()

    # Get login csrf token
    result = session_requests.get(LOGIN_URL)
    content = result.content
    soup = BeautifulSoup(content,'lxml')
    token = soup.find("input", {"name": "lt"}).get("value")

    print(token)
    # Create payload
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "lt": token,
        "execution":"e1s1",
        "_eventId":"submit"
    }

    # Perform login
    result = session_requests.post(LOGIN_URL, data = payload, headers = dict(referer = LOGIN_URL))

    URLT = URL + "%s"%(tid)
    print(URLT+"/")

    result = session_requests.get(URLT, headers = dict(referer = URLT))
    print(result.url)
    while((result.url != URLT+"/") and (result.url != "https://www.pokemon.com/us/play-pokemon/")):
        time.sleep(60)
        result = session_requests.get(URLT, headers = dict(referer = URLT))
        print(result.url)

    if(result.url == "https://www.pokemon.com/us/play-pokemon/"):
        await ctx.send("tournament id does not exist")
        print('------ END')
        return

    soup = BeautifulSoup(result.content, "lxml")
    if(soup.body.find_all(text="Access Denied")):
        print("ACCESS DENIED")
        await ctx.send("WEBSITE ACCESS DENIED")
        print('------ END')
        return

    tourny = dict(name='',idn='',category='',date='',registration='',onlinereg='',product='',premier='',
                  status='',sanctioned='',to='',venue='',address1='',address2='',city='',state='',
                  zipcode='',country='',website='',cost='',jrcost='',srcost='',macost='',
                  details='',lat='',lon='')

    fields = []
    ii=0
    while True:
        try:
            fields.append((soup.select('form fieldset li')[ii].text.encode("ascii","ignore")))
            ii = ii+1
        except IndexError:
            break

    print(tourny)
    for f in fields:
        try:
            print(f)
            proc_fields(f.decode("ascii"),tourny)
        except:
            pass
    if(len(tourny['details']) > 1024):
        tourny['details'] = tourny['details'][0:1024]

    age_cost = False
    onlinereg = False
    details = False
    if((tourny['macost'] != '') or (tourny['srcost'] != '') or (tourny['jrcost'] != '')):
        age_cost = True
    if(tourny['onlinereg'] != ''):
        onlinereg = True
    if(tourny['details'] != ''):
        details = True

    link = soup.find_all('a', {"href" : re.compile(r'http://maps.google.com/*')})

    tourny['lat'] = float(link[0].attrs['href'].split("=")[1].split(' ')[0].strip(','))
    tourny['lon'] = float(link[0].attrs['href'].split("=")[1].split(' ')[1].strip(',').strip())

    #print(tourny)
    color = 0xeee657
    ping_vg = False
    ping_tcg = False
    if("Video" in tourny['product']):
        color = 0x551a8b
        ping_vg = True
        tourny['short'] = "VG"

    elif("Trading" in tourny['product']):
        color = 0xffa500
        ping_tcg = True
        tourny['short'] = "TCG"

    embed = discord.Embed(title="%(name)s"%tourny, description="", color=color)
    embed.add_field(name="Category", value="%(category)s"%tourny)
    embed.add_field(name="Date", value="%(date)s"%tourny)
    embed.add_field(name="Registration", value="%(registration)s"%tourny)
    if(onlinereg):
        embed.add_field(name="Online Registration", value="%(onlinereg)s"%tourny)
    embed.add_field(name="Premier Event", value="%(premier)s"%tourny)
    embed.add_field(name="Status", value="%(status)s"%tourny,inline=False)
    if(age_cost):
        embed.add_field(name="JR Admission", value="%(jrcost)s"%tourny)
        embed.add_field(name="SR Admission", value="%(srcost)s"%tourny)
        embed.add_field(name="MA Admission", value="%(macost)s"%tourny)
    else:
        embed.add_field(name="Admission", value="%(cost)s"%tourny)

    if(tourny['address2'] != ''):
        loc_str = "%(venue)s\n%(address1)s\n%(city)s, %(state)s %(zipcode)s\n<https://www.google.com/maps?q=%(lat)s,+%(lon)s>"%tourny
    else:
        loc_str = "%(venue)s\n%(address1)s\n%(address2)s\n%(city)s, %(state)s %(zipcode)s\n<https://www.google.com/maps?q=%(lat)s,+%(lon)s>"%tourny
    embed.add_field(name="Location", value=loc_str,inline=False)

    embed.add_field(name="Event Website", value="<%(website)s>"%tourny,inline=False)
    embed.add_field(name="Pokemon Website", value="<%s>"%URLT,inline=False)
    tourny['url'] = URLT

    #if(details):
    #    embed.add_field(name="Details", value="%(details)s"%tourny,inline=False)

    if(time=='lookup'):
        print(tourny)
        message = await ctx.send(embed=embed)
        print("------ END")
        return

    if(time):
        tourny['time'] = str(time).encode('ascii',"ignore")
        embed.add_field(name="Carpool", value="Lot N (behind the Green Center) at **%s**"%time,inline=False)
    else:
        embed.add_field(name="Carpool", value="There will be no carpool to this event by the Mods. Comment below for any other discussion regarding the event or to organize a carpool.",inline=False)
        tourny['time'] = 'None'
    #print(str(ctx.guild.roles))

    print('------ Post to Google Calendar')
    if(cal):
        tz = tzwhere.tzwhere()
        timezone_str = tz.tzNameAt(float(tourny['lat']), float(tourny['lon'])) # Seville coordinates
        #> Europe/Madrid
        clock = tourny['registration'].split(' ')[0]
        dt_object = datetime.datetime.strptime('%s %s'%(tourny['date'],clock), '%B %d, %Y %I:%M%p')
        start_str = dt_object.strftime('%Y-%m-%dT%H:%M:%S')
        dt_object = dt_object + datetime.timedelta(hours=4)
        end_str = dt_object.strftime('%Y-%m-%dT%H:%M:%S')
        print(dt_object)
        print(start_str, end_str)

        tourny['desc'] = '%(name)s\nCategory: %(category)s\nRegistration: %(registration)s\n'%tourny
        if(onlinereg):
            tourny['desc'] = tourny['desc'] + 'Online Registration: %(onlinereg)s\n'%tourny
        tourny['desc'] = tourny['desc'] + 'Premier Event: %(premier)s\n'%tourny
        tourny['desc'] = tourny['desc'] + 'Status: %(status)s\n'%tourny
        if(age_cost):
            tourny['desc'] = tourny['desc'] + 'JR Admission: %(jrcost)s\n'%tourny
            tourny['desc'] = tourny['desc'] + 'SR Admission: %(srcost)s\n'%tourny
            tourny['desc'] = tourny['desc'] + 'MA Admission: %(macost)s\n'%tourny
        else:
            tourny['desc'] = tourny['desc'] + 'Admission: %(cost)s\n'%tourny
        if(tourny['website'] != ''):
            tourny['desc'] = tourny['desc'] + 'Event Website: <%(website)s>\n'%tourny
        tourny['desc'] = tourny['desc'] + 'Pokemon Website: <%(url)s>\n'%tourny
        tourny['desc'] = tourny['desc'] + 'Carpool: %(time)s\n'%tourny
        tourny['desc'] = tourny['desc'] + '\nNotes: %(details)s'%tourny

        if(tourny['premier'] == 'None'):
            tourny['premier'] = tourny['name']

        tourny['desc2'] = '%(venue)s %(address1)s '%tourny
        if(tourny['address2'] != ''):
            tourny['desc2'] = tourny['desc2'] + '%(address2)s '%tourny
        tourny['desc2'] = tourny['desc2'] + '%(city)s, %(state)s %(zipcode)s'%tourny

        event = {
            'summary': '%(short)s %(premier)s - %(venue)s'%tourny,
            'location': '%(desc2)s'%tourny,
            'description': '%(desc)s'%tourny,
            'start': {
                'dateTime': start_str,
                'timeZone': timezone_str,
            },
            'end': {
                'dateTime': end_str,
                'timeZone': timezone_str,
            },
        }

        event = service.events().insert(calendarId='jj6mr17pghef7bdcjnho2kj1d8@group.calendar.google.com', body=event).execute()
        print('Event created')
        embed.add_field(name="Google Calendar Link", value="<%s>"%event.get('htmlLink'),inline=False)


        print('------ END GOOGLE CALENDAR')

    # figure out the role to mention
    role = None
    everyone = None
    for r in ctx.guild.roles:
        if r.name == "TCG" and ping_tcg:
            role = r
        if r.name == "VGC" and ping_vg:
            role = r
        if r.name == "@everyone":
            everyone = r
    # create a channel for discussion about the event
    guild = ctx.message.guild

    category = None
    for cat in guild.categories:
        if cat.name == 'news':
            category = cat

    chanstr = "%(short)s-%(name)s-%(date)s"%tourny

    channel = await guild.create_text_channel(chanstr, category=category)
    await channel.set_permissions(everyone, read_messages = True,
                                      send_messages = True,
                                      read_message_history = True,
                                      embed_links = True,
                                      attach_files = True,
                                      external_emojis = True,
                                      add_reactions = True)

    message = None
    if(role):
        message = await channel.send("{}".format(role.mention),embed=embed)
    else:
        message = await channel.send(embed=embed)

    await message.add_reaction('\U0001F44D')
    await message.pin()



    print('------ END')

bot.run(TOKEN)
