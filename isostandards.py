#First Step, Create the local directory structure according to the structure.
#Second Step, according to the local directory structure, download all non-directory
#leaf.
import logging
import os
import re
import subprocess
import urllib2


DirURL = '/ittf/PubliclyAvailableStandards/ISO_IEC_14496-26_2010_Bitstreams/'
SiteAddress = 'http://standards.iso.org'
FileMarker = 'wangyixiang'


class StructureCapturer(object):
    def __init__(self,site, dir_root, local_root='scroot'):
        self._site = site
        if dir_root[-1] == '/':
            self._dir_root = dir_root
        self._local_root = local_root
        
    
    def capture(self):
        self.__capture(self._dir_root, self._local_root)
    
    def __capture(self, parent_url,  start_dir):
        url = self._site + parent_url
        try:
            f = urllib2.urlopen(url)
            data = f.read()
            items = re.findall(r'%s(.*?)">' % parent_url, data)
            if  len(items) == 0:
                logging.info("Nothing under %s ." % url)
                return
            for item in items:
                if item[-1] == '/':
                    try:
                        if not os.path.exists(os.path.join(start_dir, item)):
                            os.makedirs(os.path.join(start_dir, item))
                            logging.info('%s has been created as directory.' %\
                                         os.path.join(start_dir, item))
                        self.__capture(parent_url + item, \
                                       os.path.join(start_dir, item))
                    except OSError:
                        logging.exception('Failed on creating %s' %\
                                          os.path.join(start_dir, item))
                else:
                    try:
                        itemfile = open(os.path.join(start_dir, item), 'w')
                        itemfile.write(FileMarker)
                        itemfile.close()
                        logging.info('%s has been created as file.' %\
                                     os.path.join(start_dir, item))
                    except OSError:
                        logging.exception('Failed on creating %s' %\
                                          os.path.join(start_dir, item))                        
            return
        except Exception as e:
            logging.error("Failed on openning %s ." % url)
            return



class HttpDataSyncer(object):
    """
    Actually after we have the map captured in StructureCapturer class, it's 
    ease to get all the data we want. 
    """
    def __init__(self, dir_root, site, start_location):
        self._dir_root = dir_root
        self._site = site
        self._start_location = start_location
    
    def sync(self):
        self.__get_full_list_from_root()
        for item in self._full_list_to_download:
            try:
                f = open(item)
                data = f.read(len(FileMarker))
                f.close()
                if not data == FileMarker:
                    logging.warn("%s already contained data." % item)
                    continue
                self._get_data(item)
            except Exception:
                logging.exception("Failed on getting data for %s ." % item)
                
                
    def __get_full_list_from_root(self):
        def fill_list(parent_path):
            pathlist = os.listdir(parent_path)
            for path in pathlist:
                if not os.path.isdir(os.path.join(parent_path, path)):
                    self._full_list_to_download.append(os.path.join(\
                        parent_path, path))
                else:
                    fill_list(os.path.join(parent_path, path))

        self._full_list_to_download = []
        if self._dir_root == None:
            return
        fill_list(self._dir_root)
    
    def _get_data(self, path):
        data_url = path.replace('\\','/')[len(self._dir_root):]
        data_url = self._site + self._start_location + data_url
        self.__get_data_wget(data_url, path)
        
    
    def __get_data_wget(self, url, path):
        try:
            subprocess.check_call(['wget', '-O', path, url])
            logging.info("got data from %s to %s ." % (url, path))
        except subprocess.CalledProcessError:
            logging.exception("Failed on getting data to %s ." % path)
    
    def __get_data_curl(self):
        pass
    
    def __get_data_urllib(self):
        pass
    
    
def get_14496_26_dir_structure():
    sc = StructureCapturer(SiteAddress, DirURL)
    sc.capture()

def get_14496_26_data():
    hds = HttpDataSyncer('scroot', SiteAddress, DirURL)
    hds.sync()
    
if __name__ == '__main__':
    pass