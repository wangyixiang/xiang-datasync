#First Step, Create the local directory structure according to the structure.
#Second Step, according to the local directory structure, download all non-directory
#leaf.
import logging
import os
import urllib2
import re

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


def get_14496_26_dir_structure():
    sc = StructureCapturer(SiteAddress, DirURL)
    sc.capture()
    
if __name__ == '__main__':
    pass