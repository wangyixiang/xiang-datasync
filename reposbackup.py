import datetime
import logging
import os
import shutil
import sys
import time

from datasync import SVNRepoSyncer
from datasync import DirectorySyncer


REPOSRCDIR = r''
REPODSTDIR = r''
REPOBCKSERVERDIR = r'' + os.sep


class CISVNRepoSyncer(SVNRepoSyncer):
    def __dir_check(self, dst_repo):
        if sys.platform == 'win32':
            check_dir = os.path.normpath(dst_repo).lower()
            no_dir = REPOSRCDIR
            if check_dir == no_dir:
                return False
            return True
        return False
    
def sync_svn_repos():
    cisrs = CISVNRepoSyncer(REPOSRCDIR, REPODSTDIR)
    cisrs.excluded_repos = ['Temp_Merge']
    cisrs.sync()
    

def sync_to_backup():
    # Number of backups to keep around (0 for "keep them all")
    backup_nums = 42
    
    backup_prefix = 'SVN-'
    dst_dir = REPOBCKSERVERDIR
    dtstr = datetime.date.today().strftime('%Y%m%d')
    backup_repo_fullpath = os.path.join(dst_dir, (backup_prefix + dtstr))
    dirlist = os.listdir(dst_dir)
    repolist = []
    for adir in dirlist:
        if adir[:len(backup_prefix)] == backup_prefix:
            repolist.append(adir)
    
    repolist.sort()
    
    del repolist[max(0, len(repolist) - backup_nums):]
    
    for oldrepo in repolist:
        try:
            shutil.rmtree(os.path.join(dst_dir, oldrepo))
            logging.info('Removing old backup repo %s' % os.path.join(dst_dir, oldrepo))
        except os.error:
            logging.exception('Failed at removing old backup repo %s' %
                              os.path.join(dst_dir, oldrepo))
      
    dirsyncer = DirectorySyncer([REPODSTDIR], [backup_repo_fullpath])
    dirsyncer.depth = 100
    logging.info('Syncing of repositores backup directory started.')
    dirsyncer.sync()
    logging.info('Syncing of repositores backup directory finished. it used %f seconds'
                 % time.clock())
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    fh = logging.FileHandler('reposync.log','a')
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logging.getLogger().addHandler(fh)
    logging.getLogger().addHandler(ch)
    sync_svn_repos()
    sync_to_backup()