import logging
from colorama import Fore,Style
from colorama import init
init()

logging.basicConfig(level=logging.INFO, format=Style.BRIGHT+Fore.GREEN+'%(asctime)s' +Style.RESET_ALL+':' +Style.BRIGHT+Fore.CYAN+'%(funcName)s' +Style.RESET_ALL+':'+Style.BRIGHT+Fore.RED+'%(levelname)s'+Style.RESET_ALL+':'+Style.BRIGHT+Fore.YELLOW+'%(message)s'+Style.RESET_ALL)

import subprocess 

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

from pathlib import Path
import requests,json,base64
from pathlib import Path
import os,json,pprint,threading,re
import asyncio
import time
from pyrogram import Client,filters
from pyrogram.handlers import (
    MessageHandler,
    CallbackQueryHandler
)
from pyrogram.types import (
    Message
)
from requests.utils import quote
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
from config import *

if not TIMEOUT:
    TIMEOUT = 40

bot_msg_txt = '''
Title : <a href='{imdb}'> {name}</a>

Release : <code>{title} [{size}]</code>

Link : <a href='{drive}'>Google Drive</a>

Tags : <code>{tag}</code>
'''
START_TXT = '''
<b>BlackPearl Forum Template Generator Bot - By Dr.Luffy

Send /help for more information..!! </b>
'''
HELP_TXT ='''
<b>Nobody Gonna Help You Kek</b>

<code>THERE IS GOD,AND THERE ARE PEAKY BLINDERS
WE OWN THE ROPES,WHOSE GONNA HANG US NOW,EH?</code>
'''
AUTH_CHANNEL = set(int(x) for x in os.environ.get("AUTH_CHANNEL",CHAT_ID).split())  
AUTH_CHANNEL = list(AUTH_CHANNEL)

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


def _link_match_filt_er(link_kw: str):
    def func(flt, client, message):
        if message and message.text:
            if flt.wok in message.text:
                leech_url = None
                custom_file_name = None
                for one_entity in message.entities:
                    if one_entity.type == "url":
                        leech_url = message.text[
                            one_entity.offset:one_entity.offset + one_entity.length
                        ]
                    elif one_entity.type == "text_link":
                        leech_url = one_entity.url
                    if leech_url and flt.wok in leech_url:
                        break
                if "|" in message.text:
                    _, custom_file_name = message.text.split("|")
                if leech_url:
                    message.leech_url = leech_url.strip()
                if custom_file_name:
                    message.custom_file_name = custom_file_name.strip()
                else:
                    message.custom_file_name = None
                return True
        return False
    return filters.create(func, wok=link_kw)

	

class TemplateBot:
    def __init__(self, name="", listener=None):
        self.__G_DRIVE_TOKEN_FILE = "token.pickle"
        self.__OAUTH_SCOPE = ['https://www.googleapis.com/auth/drive']
        self.__service = self.authorize()
        self.INDEX_BASE_URL = INDEX_URL
        self.path = []
        self.TMDB_API = TMDB_API
        self.OMDB_API = OMDB_API
        self.DRIVE_ID = DRIVE_ID
        self.TIMEOUT = TIMEOUT
        self.bot_message = bot_msg_txt

    def get_readable_file_size(self, size_in_bytes) -> str:
        if size_in_bytes is None:
            return '0B'
        index = 0
        size_in_bytes = int(size_in_bytes)
        while size_in_bytes >= 1024:
            size_in_bytes /= 1024
            index += 1
        try:
            return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
        except IndexError:
            return 'File too large'

    def authorize(self):
        # Get credentials
        credentials = None
        if os.path.exists(self.__G_DRIVE_TOKEN_FILE):
            with open(self.__G_DRIVE_TOKEN_FILE, 'rb') as f:
                credentials = pickle.load(f)
        if credentials is None or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.__OAUTH_SCOPE)
                credentials = flow.run_console(port=0)

            # Save the credentials for the next run
            with open(self.__G_DRIVE_TOKEN_FILE, 'wb') as token:
                pickle.dump(credentials, token)
        return build('drive', 'v3', credentials=credentials, cache_discovery=False)
    
    def getTags(self,IMDB,FILENAME):
    	self.TAGS = ''
    	self.FILENAME = FILENAME
    	self.IMDB = IMDB
    	try:
    		self.Genre = ''
    		self.Genre = self.IMDB['Genre']
    		if self.Genre!='N/A':
    			self.TAGS+=f"{self.Genre},"
    	except KeyError:
    		print("No Genre Found From OMDB")
    	QUALITY_TAGS = ['1080p','2160p','720p','480p','4k']
    	DDPTAGS =['DDP5.1','DD+5.1','DDP 5.1','DD+ 5.1','ddp 5.1']
    	DVTAGS = ['DV','DoVi','Dolby Vision']
    	AMZNTAGS = ['AMZN']
    	NFTAG =['NF','Netflix']
    	DSNPTAG = ['DSNP','HS','HOTSTAR','DSNY+']
    	APPLETAG= ['APPLETV','ATVP','APTV','AppleTv']
    	BLURAYTAG = ['Blu-Ray','Bluray','BD','BLURAY','bluray','blu ray','Blu Ray']
    	HDRTAG = ['HDR','hdr']
    	DDP_TAGS =['DDP2.0','DD+2.0','DDP 2.0','DD+ 2.0','DDP.2.0']
    	AACTAGS =['AAC5.1','AAC 5.1','AAC.5.1']
    	AAC_TAGS =['AAC2.0','AAC 2.0','AAC.2.0']
    	HEVCTAG = ['HEVC','H.265','H265','x265']
    	H264TAG = ['H.264','H264','AVC','x264']
    	for i in APPLETAG:
    		if i in self.FILENAME:
    			self.TAGS+="atvp,web-dl,"
    	for i in BLURAYTAG:
    		if i in self.FILENAME:
    			self.TAGS+="blu-ray,"
    	for i in H264TAG:
    		if i in self.FILENAME:
    			self.TAGS+="h264,"
    	for i in HEVCTAG:
    		if i in self.FILENAME:
    			self.TAGS+="hevc,h265,"
    	for i in HDRTAG:
    		if i in self.FILENAME:
    			self.TAGS+="hdr,"
    	for i in DSNPTAG:
    		if i in self.FILENAME:
    			self.TAGS+="dsnp,web-dl,"
    	for i in NFTAG:
    		if i in self.FILENAME:
    			self.TAGS+=f"nf web-dl,"
    	for i in AMZNTAGS:
    		if i in self.FILENAME:
    			self.TAGS+=f"amzn web-dl,"
    	for i in DVTAGS:
    		if i in self.FILENAME:
    			self.TAGS+=f"dolby vision,"
    	for i in QUALITY_TAGS:
    		if i in self.FILENAME:
    			self.TAGS+=f"{i},"
    	for i in DDPTAGS:
    		if i in self.FILENAME:
    			self.TAGS+="ddp 5.1,"
    	for i in DDP_TAGS:
    		if i in self.FILENAME:
    			self.TAGS+="ddp 2.0,"
    	for i in AACTAGS:
    		if i in self.FILENAME:
    			self.TAGS+="aac 5.1,"
    	for i in AAC_TAGS:
    		if i in self.FILENAME:
    			self.TAGS+="aac 2.0,"
    	return self.TAGS


    def getOMDB(self,FILENAME):
    	self.IMDB_NAME =''
    	self.IMDB_YEAR =''
    	self.TITLE =''
    	self.FILENAME = FILENAME
    	
    	if self.IMDB_NAME =='':
    		try:
    			logging.info("Looking For Year From File Name")
    			self.IMDB_YEAR = '&y=' + re.findall(r'(19\d{2}|20\d{2})', self.FILENAME)[-1]
    			logging.info(f"Found YEAR : {self.IMDB_YEAR}")
    		except:
    			self.IMDB_YEAR=''
    			logging.info("Year Not Found From File")
    	logging.info("Getting OMDB Name From File Name")
    	self.TITLE_OMDB = re.sub('[^a-zA-Z0-9]', '+', os.path.basename(self.FILENAME)).split('+' + self.IMDB_YEAR.replace('&y=', '') + '+')[0].split('+S0')[0].split('+S1')[0].split('+S2')[0].split('+1080p')[0].split('+2160p')[0].split('+UHD')[0].split('+REPACK')[0].split('+HYBRID')[0].split('+EXTENDED')[0]
    	logging.info(f"Found Title : {self.TITLE_OMDB}")
    	return self.TITLE_OMDB,self.IMDB_YEAR
    	
    def getBBCODE(self,IMDB):
    	logging.info("Merging Everything to BBCODE")
    	self.BBCODE=''
    	self.IMDBPoster =''
    	self.Backdrop = None
    	self.TMDB = None
    	self.IMDB = IMDB
    	try:
    	    self.TMDB = requests.get(f"https://api.themoviedb.org/3/find/{self.IMDB['imdbID']}?api_key={self.TMDB_API}&external_source=imdb_id").json()
    	    if len(self.TMDB['movie_results']) != 0:
    	        self.TMDB = self.TMDB['movie_results'][0]
    	        self.TMDB['type'] = 'movie'
    	        self.TMDB_NAME = self.TMDB['title']
    	        self.TMDB_YEAR = self.TMDB['release_date'][0:4]
    	    elif len(self.TMDB['tv_results']) != 0:
    	        self.TMDB = self.TMDB['tv_results'][0]
    	        self.TMDB['type'] = 'tv'
    	        self.TMDB_NAME = self.TMDB['name']
    	        self.TMDB_YEAR = self.TMDB['first_air_date'][0:4]
    	    else:
    	        self.TMDB = None
    	    if self.TMDB is not None:
    	        logging.info(f"TMDB Link: 'https://www.themoviedb.org/{self.TMDB['type']}/{self.TMDB['id']}'")
    	        self.IMDB_NAME = f"{self.TMDB_NAME} ({self.TMDB_YEAR})"
    	        self.IMDBPoster = f"https://image.tmdb.org/t/p/original{self.TMDB['poster_path']}"
    	        self.Backdrop = f"https://image.tmdb.org/t/p/original{self.TMDB['backdrop_path']}"
    	        self.BBCODE = f"[CENTER][URL='{self.IMDBPoster}'][IMG WIDTH='350px']{self.IMDBPoster}[/IMG][/URL][/CENTER]\n"
    	except Exception as e:
                    logging.error(e)
                    if ('Poster' in self.IMDB and self.IMDB['Poster'] != 'N/A'):
                    	self.IMDBPoster = re.sub('_V1_SX\d+.jpg', '_V1_SX1000.png', self.IMDB['Poster'])
                    	logging.info("Attaching Poster From OMDB")
                    	self.BBCODE = f"[CENTER][URL='{self.IMDBPoster}'][IMG WIDTH='350px']{self.IMDBPoster}[/IMG][/URL][/CENTER]\n"
    	#print(self.IMDB)
    	self.BBCODE += f"[CENTER][URL='https://blackpearl.biz/search/1/?q={self.IMDB['imdbID']}&o=date'][FORUMCOLOR][B][SIZE=6]{self.IMDB_NAME}[/SIZE][/B][/FORUMCOLOR][/URL][/CENTER]\n"
    	self.BBCODE += f"[CENTER][URL='https://imdb.com/title/{self.IMDB['imdbID']}'][IMG WIDTH='46px']https://ia.media-imdb.com/images/M/MV5BMTk3ODA4Mjc0NF5BMl5BcG5nXkFtZTgwNDc1MzQ2OTE@.png[/IMG][/URL][/CENTER]"
    	self.BBCODE += f"[HR][/HR][INDENT][SIZE=6][FORUMCOLOR][B]Plot Summary :[/B][/FORUMCOLOR][/SIZE]\n\n[JUSTIFY]{self.IMDB['Plot']}[/JUSTIFY][/INDENT]" if ('Plot' in self.IMDB and self.IMDB['Plot'] != 'N/A') else ''
    	if ('Type' in self.IMDB and self.IMDB['Type'] == 'movie'):
    		self.IMDB['Type'] = 'Movie'
    	elif ('Type' in self.IMDB and self.IMDB['Type'] == 'series'):
    	 	self.IMDB['Type'] = 'TV Show'
    	else:
    	 	self.IMDB['Type'] = 'IMDB'
    	 #
    	self.BBCODE += f"[HR][/HR][INDENT][SIZE=6][FORUMCOLOR][B]{self.IMDB['Type']} Info :[/B][/FORUMCOLOR][/SIZE][/INDENT]\n[LIST]"
    	self.BBCODE += f"[*][FORUMCOLOR][B]self.IMDB :[/B][/FORUMCOLOR] {self.IMDB['IMDBRating']} ({self.IMDB['IMDBVotes']})\n" if ('IMDBRating' in self.IMDB and self.IMDB['IMDBRating'] != 'N/A' and 'IMDBVotes' in self.IMDB and self.IMDB['IMDBVotes'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Rated :[/B][/FORUMCOLOR] {self.IMDB['Rated']}\n" if ('Rated' in self.IMDB and self.IMDB['Rated'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]self.Genres :[/B][/FORUMCOLOR] {self.IMDB['Genre']}\n" if ('Genre' in self.IMDB and self.IMDB['Genre'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Awards :[/B][/FORUMCOLOR] {self.IMDB['Awards']}\n" if ('Awards' in self.IMDB and self.IMDB['Awards'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Runtime :[/B][/FORUMCOLOR] {self.IMDB['Runtime']}\n" if ('Runtime' in self.IMDB and self.IMDB['Runtime'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Starring :[/B][/FORUMCOLOR] {self.IMDB['Actors']}\n" if ('Actors' in self.IMDB and self.IMDB['Actors'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Countries :[/B][/FORUMCOLOR] {self.IMDB['Country']}\n" if ('Country' in self.IMDB and self.IMDB['Country'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Languages :[/B][/FORUMCOLOR] {self.IMDB['Language']}\n" if ('Language' in self.IMDB and self.IMDB['Language'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Written By :[/B][/FORUMCOLOR] {self.IMDB['Writer']}\n" if ('Writer' in self.IMDB and self.IMDB['Writer'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Directed By :[/B][/FORUMCOLOR] {self.IMDB['Director']}\n" if ('Director' in self.IMDB and self.IMDB['Director'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Release Date :[/B][/FORUMCOLOR] {self.IMDB['Released']}\n" if ('Released' in self.IMDB and self.IMDB['Released'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Production By :[/B][/FORUMCOLOR] {self.IMDB['Production']}\n" if ('Production' in self.IMDB and self.IMDB['Production'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]DVD Release Date:[/B][/FORUMCOLOR] {self.IMDB['DVD']}\n" if ('DVD' in self.IMDB and self.IMDB['DVD'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Official Website :[/B][/FORUMCOLOR] {self.IMDB['Website']}\n" if ('Website' in self.IMDB and self.IMDB['Website'] != 'N/A') else ''
    	self.BBCODE += f"[*][FORUMCOLOR][B]Box Office Collection :[/B][/FORUMCOLOR] {self.IMDB['BoxOffice']}[/LIST]" if ('BoxOffice' in self.IMDB and self.IMDB['BoxOffice'] != 'N/A') else '[/LIST]'
    	self.BBCODE = self.BBCODE.replace('[HR][/HR][INDENT][SIZE=6][FORUMCOLOR][B]IMDB Info :[/B][/FORUMCOLOR][/SIZE][/INDENT]\n[LIST][/LIST]', '')
    	self.BBCODE += '[HR][/HR][INDENT][SIZE=6][FORUMCOLOR][B]Media Info :[/B][/FORUMCOLOR][/SIZE][/INDENT]'
    	logging.info("Attaching Media Info")
    	self.BBCODE += f"[SPOILER='Media Info'][CODE TITLE='Media Info']{self.mediainfo_txt}[/CODE][/SPOILER]\n"
    	logging.info("Attaching Download Link")
    	self.BBCODE += f'[HR][/HR][INDENT][SIZE=6][FORUMCOLOR][B]Download Link :[/B][/FORUMCOLOR][/SIZE][/INDENT]\n[CENTER][HIDEREACTSCORE=20][HIDEREACT=1,2,3,4,5,6,7,8][DOWNCLOUD]{self.gdrive_link}[/DOWNCLOUD][/HIDEREACT][/HIDEREACTSCORE][/CENTER]'
    	return self.BBCODE,self.Backdrop

    def getMediaInfo(self,file,media_name):
        self.mediainfo_txt = ""
        self.mediainfo_file = file
        self.media_name = media_name
        self.mediainfoexe = "mediainfo"
        self.mi_cmd = f"{self.mediainfoexe} \"{self.mediainfo_file}\""
        time.sleep(4)
        self.mediainfo_cmd = subprocess.Popen(self.mi_cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = self.mediainfo_cmd.communicate()
        self.mediainfo_txt = out.decode().strip()
        self.errors = err.decode().strip()
        if self.errors:
            logging.error(self.errors)
        if "General" in self.mediainfo_txt:
            print("Grabbed Mediainfo")
            self.mediainfo_txt = self.mediainfo_txt.replace(self.mediainfo_file,self.media_name)
            return True
        else:
            return False
    def getResp(self,query):
        self.query = query
        response = self.__service.files().list(
            supportsTeamDrives=IS_TD,
            includeTeamDriveItems=IS_TD,
            q=query,
            spaces='drive',
            pageSize=200,
            fields='files(id, name, mimeType, size)',
            orderBy='modifiedTime desc').execute()["files"]
        return response
    def drive_query(self, parent_id, fileName):
        fileName = fileName.replace("'","\\'").replace('"','\\"')
        gquery = " and ".join([f"name contains '{x}'" for x in fileName.split()])
        query = f"'{parent_id}' in parents and ({gquery})"
        resp = self.getResp(query)
        return resp
        
    def getIndex(self,mainfolder=None,subfolder=None,filename=None):
        self.mainfolder = mainfolder
        self.subfolder = subfolder
        self.Filename = str(filename)
        self.Filename = quote(self.Filename)
        if self.Filename:
            self.INDEX_FILE = f"{self.INDEX_BASE_URL}/"
            if self.mainfolder:
                self.INDEX_FILE += f"{self.mainfolder}/"
            if self.subfolder:
                self.INDEX_FILE += f"{self.subfolder}/"
            self.INDEX_FILE += f"{self.Filename}"
            return self.INDEX_FILE
        return None
            
        
    def getDriveLink(self,FileId,Folder=False):
        self.FileId = FileId
        self.gdriveLink = None
        self.BaseFolderLink = "https://drive.google.com/drive/folders/{}?usp=sharing"
        self.BaseFileLink = "https://drive.google.com/file/d/{}/view?usp=sharing"
        if Folder:
            self.gdriveLink = self.BaseFolderLink.format(self.FileId)
        else:
            self.gdriveLink = self.BaseFileLink.format(self.FileId)
        return self.gdriveLink
        
    def getList(self,parent_id):
        query = f"'{parent_id}' in parents"
        resp = self.getResp(query)
        return resp
    def getGDrive(self,FileName):
        self.Found = None
        self.list_results = []
        self.results = []
        self.FileName = str(FileName)
        self.isFolder = False
        self.fileid = None
        self.isFolder = False
        self.parent_id = str(DRIVE_ID)
        self.results = self.drive_query(self.parent_id,self.FileName)
        if self.results:
            for file in self.results:
                if file['name'] == self.FileName:
                    self.fileid = file['id']
                    if file['mimeType'] == "application/vnd.google-apps.folder":
                        self.isFolder = True
                    else:
                        self.isFolder = False
    async def ParseFiles(self,client,message):
        self.client = client
        self.message = message
        self.reply_to_id = self.message.message_id
        self.user_id = self.message.from_user.id
        self.file_name = None
        self.File_ID = None
        self.list_results = self.getList(self.fileid)
        if self.list_results:
            for files in self.list_results:
                subfolder =None
                mainfolder = self.FileName
                print(Style.BRIGHT+"===========================================================")
                self.IMDBID = None
                self.IMDBURL = None
                self.isFolder = False
                self.file_name = files['name']
                logging.info(self.file_name)
                msgtxt = f"Started Fetching BBCODE\nTitle : <b>{self.file_name}</b>"
                self.status_message = await self.message.reply_text(msgtxt)
                self.file_Name = self.file_name
                #print(files)
                try:
                    self.FileSize = int(files['size'])
                except KeyError:
                    logging.error("No size found")
                    self.FileSize = int()
                self.File_ID = files['id']
                self.permissions = {"role":"reader","type":"anyone"}
                self.__service.permissions().create(supportsTeamDrives=IS_TD,fileId=self.File_ID,body=self.permissions).execute()
                if files['mimeType'] == "application/vnd.google-apps.folder":
                    self.isFolder =True
                    logging.warning("Folder found")
                if self.isFolder:
                    self.File_ID = files['id']
                    logging.info("Parsing folder contents")
                    self.folderFiles = self.getList(self.File_ID)
                    self.Fsize = int()
                    self.FolderSize = int()
                    if self.folderFiles:
                        for File in self.folderFiles:
                            #print(File)
                            try:
                                self.FSize = File['size']
                                self.FolderSize += int(self.FSize)
                                #logging.info(self.FolderSize)
                            except KeyError:
                                pass
                            
                            if "E01" in File['name']:
                                folderName = self.file_name
                                File_Name = File['name']
                                subfolder = folderName
                                self.file_Name = File_Name
                                
                if self.file_Name:
                    self.index_url = self.getIndex(mainfolder=mainfolder,subfolder=subfolder,filename=self.file_Name)
                if self.index_url:
                    for i in range(0,4):
                        self.MediaiNfo = self.getMediaInfo(self.index_url,self.file_Name)
                        if self.MediaiNfo:
                            break
                if self.File_ID:
                    self.gdrive_link = self.getDriveLink(self.File_ID,Folder=self.isFolder)
                    if self.FileSize:
                        self.file_size = int(self.FileSize)
                    elif self.FolderSize:
                        self.file_size = int(self.FolderSize)
                    else:
                        self.file_size = ''
                    if self.file_size:
                        self.file_size = self.get_readable_file_size(self.file_size)
                        logging.info(f"Size : {self.file_size}")
                   # print(self.file_name,"-",self.file_size,"-",self.gdrive_link)
                if self.gdrive_link:
                    self.NAME,self.YEAR = self.getOMDB(self.file_name)
                    if self.NAME:
                        self.IMDB = requests.get(f'http://www.omdbapi.com/?t={self.NAME}{self.YEAR}&apikey={self.OMDB_API}&r=json').json()
                        if self.IMDB['Response'] == 'False':
                            self.status = await self.message.reply_text(f"SEND IMDB Within {self.TIMEOUT}sec")
                            await asyncio.sleep(self.TIMEOUT)
                            for i in range(0,self.TIMEOUT):
                                u_id = self.status.message_id + 1
                                m = await self.client.get_messages(self.message.chat.id ,u_id)
                                if m.text is not None and m.from_user.id == self.user_id:
                                    for one_entity in m.entities:
                                        if one_entity.url is not None and one_entity.url.lower().startswith("https://www.imdb"):
                                            self.IMDBURL = str(one_entity.url)
                                            self.IMDBID = self.IMDBURL.split("/tt")[1]
                                            await self.status.delete()
                                            await m.delete()
                                            await self.status_message.reply_text(f"<b>Fetching INFO</b>\nIMDB : <i>{self.IMDBURL}</i>")
                                            self.IMDB = requests.get(f'http://www.omdbapi.com/?i=tt{self.IMDBID}&apikey={self.OMDB_API}&r=json').json()
                                            break
                                    break
                if self.IMDB:
                    if self.IMDB['Response'] == 'True':
                        self.IMDBID = self.IMDB['imdbID']
                        self.IMDBURL = f"https://www.imdb.com/title/{self.IMDBID}"
                        self.BBCODE,self.Backdrop = self.getBBCODE(self.IMDB)
                        self.FILE_TAGS = self.getTags(self.IMDB,self.file_Name)
                        self.BBCODE_TXT = os.getcwd()+f"/BlackPearl.txt"
                        with open(self.BBCODE_TXT,'w',encoding='UTF-8') as f:
                            logging.info(f"Saving BBCODE -> {self.BBCODE_TXT}")
                            f.write(self.BBCODE)
                        if os.path.exists(self.BBCODE_TXT):
                            self.final_msg = self.bot_message.format(name=self.IMDB_NAME,title=self.file_name.replace(".mkv","").replace(".mp4","").replace(".avi",""),size=self.file_size,drive=self.gdrive_link,imdb=self.IMDBURL,tag=self.FILE_TAGS)
                            await self.status_message.delete()
                            await client.send_document(
                                chat_id=message.chat.id,
                                document=self.BBCODE_TXT,
                                caption=self.final_msg,
                                reply_to_message_id=self.reply_to_id
                                )
                        else:
                            return
                        
                    else:
                        return
                                
                                
                    
        else:
            return None
    async def main(self,client,message,FileName=None):
        self.FileName = FileName
        self.user_id = message.from_user.id
        self.getGDrive(self.FileName)
        await self.ParseFiles(client,message)
        
async def BBCODEbot(client,message):
    logging.info("Started BlackPearl Template Bot by Dr.Luffy")
    drive = TemplateBot()
    msg = message.text
    if BOT_CMD in msg:
        filePath = msg.replace(f"{BOT_CMD} ","")
        if filePath:
            await drive.main(client,message,FileName=filePath)
    elif HELP_CMD in msg:
        await message.reply_text(HELP_TXT)
    elif START_CMD in msg:
        await message.reply_text(START_TXT)
    else:
        return
        
        
if __name__ == "__main__" :
 app2 = Client(
        "himessage",
        bot_token=TG_BOT_TOKEN,
        api_id=APP_ID,
        api_hash=API_HASH
    )

 bpbot = MessageHandler(BBCODEbot,
 filters=filters.chat(chats=AUTH_CHANNEL) & (_link_match_filt_er(START_CMD) | _link_match_filt_er(HELP_CMD) | _link_match_filt_er(BOT_CMD)))
 
app2.add_handler(bpbot)
app2.run()
