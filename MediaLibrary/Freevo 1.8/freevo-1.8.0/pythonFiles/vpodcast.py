# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Video Podcast Player Plug-in
# -----------------------------------------------------------------------
# $Id: vpodcast.py 10105 2007-11-11 18:01:39Z duncan $
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al.
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------

__author__ = 'Krasimir Atanasov'
__author_email__ = 'atanasov.krasimir@gmail.com'

import urllib2, os, threading, urllib, time, re, string
import config, menu, rc, plugin, util, skin
import util.feedparser
from item import Item
from audio.player import PlayerGUI
from video.videoitem import VideoItem
from menu import MenuItem
from gui import AlertBox, PopupBox, GUIObject
from event import *
#import youtube-dl

MAX_AGE = 3600 * 10

_player_ = None



class PluginInterface(plugin.MainMenuPlugin):

    """
    Video podcast plugin

    Add to local_conf.py
    | plugin.activate('video.vpodcast')
    | VPODCAST_LOCATIONS = [
    |     ('You Tube - Top Viewed', 'http://youtube.com/rss/global/top_viewed.rss'),
    |     ('You Tube - Norah Jones', 'http://www.referd.info/tag/norah_jones/rss.php'),
    |     ('You Tube - Top Rated', 'http://youtube.com/rss/global/top_rated.rss'),
    |     ('Metacafe - Top Videos', 'http://www.metacafe.com/tags/top_videos/rss.xml'),
    |     ('Metacafe - Music', 'http://www.metacafe.com/tags/music/rss.xml'),
    |     ('Metacafe - Today Videos ', 'http://www.metacafe.com/rss/today_videos/rss.xml'),
    |     ('Metacafe - New Videos', 'http://www.metacafe.com/rss/new_videos.rss'),
    |     ('CNN - Now in the news', 'http://rss.cnn.com/services/podcasting/nitn/rss.xml'),
    |     ('CNN - The Larry King', 'http://rss.cnn.com/services/podcasting/lkl/rss?format=xml'),
    |     ('Discovery Chanel', 'http://www.discovery.com/radio/xml/discovery_video.xml')
    | ]
    |
    | VPODCAST_DIR = '/home/user_name/VPODCAST'
    """
    def __init__(self):
        """ Initialise the Video postcast plug-in interface """
        plugin.MainMenuPlugin.__init__(self)
        self.plugin_name = 'vpodcast'
        self.check_dir()


    def config(self):
        """ freevo plugins -i audio.vpodcast returns the info """
        return [
            ('VPODCAST_LOCATIONS', None, 'List of podcast locations'),
            ('VPODCAST_DIR', None, 'Directory for downloaded podcasts')
        ]


    def items(self, parent):
        return [ VPodcastMainMenuItem(parent) ]


    def check_dir(self):
        """ Check that the VPODCAST_DIR directories exist, if not create them """
        if not os.path.isdir(config.VPODCAST_DIR):
            _debug_('%r does not exist, directory created' % (config.VPODCAST_DIR))
            os.makedirs(config.VPODCAST_DIR)

        for pcdir in config.VPODCAST_LOCATIONS:
            pc_dir = config.VPODCAST_DIR + '/' + pcdir[0]
            if not os.path.isdir(pc_dir):
                os.makedirs(pc_dir)


class VPVideoItem(VideoItem):
    """
    Video podcast video item
    """
    def __init__(self, name, url, parent):
        """ Initialise the VPVideoItem class """
        self.vp_url = url
        url = name
        VideoItem.__init__(self, name, parent)


    def play(self, arg=None, menuw=None):
        """ Play this Podcast"""

        # play the item.
        isYT = self.vp_url.find('youtube.com')  #YouTube podcast
        isMC = self.vp_url.find('metacafe.com') #Metacafe podcast

        if isYT != -1:
            self.download_url = self.youtube(self.vp_url)

        elif isMC != -1:
            self.download_url = self.metacafe(self.vp_url)

        else:
            self.download_url = self.vp_url

        if not os.path.exists(self.filename):
            background = BGDownload(self.download_url, self.filename)
            background.start()
            popup = PopupBox(text=_('Buffering podcast...'))
            popup.show()
            time.sleep(20) # 20s. buffering time
            popup.destroy()

        # call the play funuction of VideoItem
        VideoItem.play(self, menuw=menuw, arg=arg)


    def youtube(self, url):
        const_video_url_str = 'http://www.youtube.com/watch?v=%s'
        const_video_url_re = re.compile(r'^((?:http://)?(?:\w+\.)?youtube\.com/(?:v/|(?:watch(?:\.php)?)?\?(?:.+&)?v=))?([0-9A-Za-z_-]+)(?(1)[&/].*)?$')
        const_url_t_param_re = re.compile(r'[,{]t:\'([^\']*)\'')
        const_video_url_real_str = 'http://www.youtube.com/get_video?video_id=%s&t=%s'
        const_video_title_re = re.compile(r'<title>YouTube - ([^<]*)</title>', re.M | re.I)
        try:
            video_url_mo = const_video_url_re.match(url)
            video_url_id = video_url_mo.group(2)
            video_url = const_video_url_str % video_url_id
            # Retrieve video webpage
            video_webpage = urllib.urlopen(video_url).read()
            match = const_url_t_param_re.search(video_webpage)
            if match is None:
                print 'step_error'
            video_url_t_param = match.group(1)
            # Retrieve real video URL
            video_url_real = const_video_url_real_str % (video_url_id, video_url_t_param)
            return video_url_real
        except:
            print 'Error YouTube URL'


    def metacafe(self, url):
        video_url =  url
        const_video_url_re = re.compile(r'(?:http://)?(?:www\.)?metacafe\.com/watch/([^/]+)/([^/]+/)?.*')
        const_normalized_url_str = 'http://www.metacafe.com/watch/%s/'
        const_age_post_data = r'allowAdultContent=1&submit=Continue+-+I%27m+over+18'
        const_video_mediaurl_re = re.compile(r'&mediaURL=([^&]+)&', re.M)

        try:
            # Verify video URL format and extract URL data to normalize URL
            video_url_mo = const_video_url_re.match(video_url)
            if video_url_mo is None:
                sys.exit('Error: URL does not seem to be a metacafe video URL. If it is, report a bug.')
            video_url_id = video_url_mo.group(1)
            video_url_title = (video_url_mo.group(2) is not None) and video_url_mo.group(2)[:-1] or None
            video_url = const_normalized_url_str % video_url_id

            # Retrieve video webpage
            video_webpage = urllib.urlopen(video_url).read()
            # Retrieve real video URL
            video_url_real = self.extract_step('Extracting real video URL', 'unable to extract real video URL', \
                const_video_mediaurl_re, video_webpage)
            return video_url_real
        except:
            print 'Error Metacafe URL'


    def extract_step(self, step_title, step_error, regexp, data):
        try:
            match = regexp.search(data)
            if match is None:
                error_advice_exit(step_error)

            extracted_data = match.group(1)

            return extracted_data

        except KeyboardInterrupt:
            sys.exit('\n')



class VPodcastMainMenuItem(MenuItem):
    """
    this is the item for the main menu and creates the list
    of commands in a submenu.
    """
    def __init__(self, parent):
        MenuItem.__init__(self, parent, arg='audio', skin_type='radio')
        self.name = _('Video Podcast')


    def actions(self):
        """ return a list of actions for this item """
        return [ (self.create_podcast_menu, 'stations') ]


    def create_podcast_submenu(self, arg=None, menuw=None, image=None):
        """ create the sub-menu for the podcast """
        popup = PopupBox(text=_('Fetching podcast...'))
        popup.show()
        url = arg[1]
        p = podcast()
        p.open_rss(url)
        p.rss_title()
        p.rss_count()

        podcast_items = []
        for pc_location in range(p.rss.count):
            p.rss_item(pc_location)
            if p.image != None:
                image = config.VPODCAST_DIR + '/' + arg[0] + '/' + p.title + '.jpg'
                self.download(p.image, image)
            else:
                image = None
            url = p.link
            name = p.title
            if url != 'ERROR':
                isYT = url.find('youtube.com')
                isMC = url.find('metacafe.com')
                if isYT == -1 and isMC == -1:
                    file_ext = '.avi'
                else:
                    file_ext = '.flv'

                filename  = config.VPODCAST_DIR + '/' + arg[0] + '/' + name + file_ext
                podcast_items += [menu.MenuItem(_(p.title), \
                    action=VPVideoItem(filename, url, self), arg=None, image=image)]

        popup.destroy()
        if (len(podcast_items) == 0):
            podcast_items += [menu.MenuItem(_('No Podcast locations found'),
                                             menwu.goto_prev_page, 0)]
        podcast_sub_menu = menu.Menu(_('Video Podcasts'), podcast_items)
        rc.app(None)
        menuw.pushmenu(podcast_sub_menu)
        menuw.refresh()


    def create_podcast_menu(self, arg=None, menuw=None):
        """ Create the main menu item for the video podcasts """
        popup = PopupBox(text=_('Fetching podcasts...'))
        popup.show()
        podcast_menu_items = []

        for location in config.VPODCAST_LOCATIONS:
            url = location[1]
            image_path = config.VPODCAST_DIR + '/' + location[0] + '/' + 'cover.jpg'
            if self.check_logo(image_path):
                p = podcast()
                p.open_rss(url)
                p.rss_title()
                name = p.rss_title
                try:
                    image_url = p.rss_image
                    self.download(image_url, image_path)
                except:
                    print 'No image in RSS'

            if (len(config.VPODCAST_DIR) == 0):
                podcast_items += [menu.MenuItem(_('Set VPODCAST_DIR in local_conf.py'), menwu.goto_prev_page, 0)]

            podcast_menu_items += [menu.MenuItem(_(location[0]), action=self.create_podcast_submenu, \
                arg=location, image=image_path)]

        popup.destroy()
        podcast_main_menu = menu.Menu(_('Video Podcasts'), podcast_menu_items)
        rc.app(None)
        menuw.pushmenu(podcast_main_menu)
        menuw.refresh()


    def download(self, url, savefile):
        """ Download the url and save it """
        file = urllib2.urlopen(url).read()
        save = open(savefile, 'w')
        print >> save, file
        save.close()


    def check_logo(self, logo_file):
        """ Check if the logo has changed """
        if os.path.exists(logo_file) == 0 or (abs(time.time() - os.path.getmtime(logo_file)) > MAX_AGE):
            return True
        else:
            return False



class podcast:
    """
    """
    def __init__(self):
        pass


    def open_rss(self, url):
        self.rss = util.feedparser.parse(url)
        self.encoding = self.rss.encoding


    def rss_title(self):
        try:
            self.rss_title = self.rss.feed.title.encode(self.encoding)

            #self.rss_date = self.rss.feed.date
        except:
            print 'Error rss_title'
            self.rss_title = None

        try:
            self.rss_description = self.rss.feed.description.encode(self.encoding)
        except:
            print 'Error rss_description'

        try:
            self.rss_image = self.rss.feed.image.url
        except:
            self.rss_image = None


    def rss_count(self):
        self.rss.count =  len(self.rss.entries)


    def rss_item(self, item=0):

        try:
            self.title = self.rss.entries[item].title.encode(self.encoding)
            self.title = re.sub('(/)','_',self.title)
            description_all = self.rss.entries[item].description
            self.link = self.rss.entries[item].link
            # Search for image
            #img_pattern = '<img src="(.*?)" align='
            img_pattern = 'img src="(.*?)"'
            try:
                self.image = re.search(img_pattern, description_all).group(1)
            except:
                self.image = None

        except:
            pass

        if self.link == None:
            self.link = 'ERROR'



class BGDownload(threading.Thread):
    """
    Download file in background
    """
    def __init__(self, url, savefile):
        threading.Thread.__init__(self)
        self.url = url
        self.savefile = savefile


    def run(self):
        try:
            file = urllib2.urlopen(self.url)
            info = file.info()
            save = open(self.savefile, 'wb')
            chunkSize = 25
            totalBytes = int(info['Content-Length'])
            downloadBytes = 0
            bytesLeft = totalBytes
            while bytesLeft > 0:
                chunk = file.read(chunkSize)
                readBytes = len(chunk)
                downloadBytes += readBytes
                bytesLeft -= readBytes
                save.write(chunk)
        except:
            print 'Download Error !'
