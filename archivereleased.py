# -*- coding=utf-8 -*-

#将age大于90天的文件打包
#打包格式，标准zip
#打包过的目录删除以节省空间
#对目录的删除必须使用完整的绝对路径，并且只能以专属文件夹为开头名
#必须log
#先完成测试部分的代码

#Debug 判断文件夹age, 对文件夹进行压缩
#Warn  碰到非标准结构的目录
#Error 压缩失败，文件夹删除失败

import datetime
import logging
import os
import subprocess
import sys
import shutil

class WrongArgument(Exception): pass

class ArchiveDeliveryDirectory(object):
    def __init__(self):
        pass
        
    def _packit(self, pack_dirname, package_name):
        self.__7zipit(pack_dirname, package_name)
    
    def __7zipit(self, zip_dirname, zip_filename, stay_at_zip_parent_dir=True):
        """
        wrapper 7 zip for command line edition for packing.
        7z <command> [<switch>...] <base_archive_name> [<arguments>...]
        
        7z a archive1.zip subdir\

        adds all files and subfolders from folder subdir to archive archive1.zip.
        The filenames in archive !!will contain!! subdir\ prefix.

        7z a archive2.zip .\subdir\*

        adds all files and subfolders from folder subdir to archive archive2.zip. 
        The filenames in archive !!will not contain!! subdir\ prefix.

        Switches that can be used with this command
        -i (Include)
        -m (Method)
        -p (Set Password)
        -r (Recurse)
        -sfx (create SFX)
        -si (use StdIn)
        -so (use StdOut)
        -ssw (Compress shared files)
        -t (Type of archive)
        -u (Update)
        -v (Volumes)
        -w (Working Dir)
        -x (Exclude) 
        """
        bin_cmd = '7z'
        cmd = 'a'
        archive_type = '-tzip'
        recurse = '-r'
        zip_filename = ''.join([zip_filename, '.zip'])
        if stay_at_zip_parent_dir == True:
            zip_parent_dirname = os.path.dirname(zip_dirname)
            zip_filename = ''.join([zip_parent_dirname, os.sep, zip_filename])
        try:        
            subprocess.check_call([bin_cmd, cmd, archive_type, recurse, \
                                   zip_filename, zip_dirname])
            logging.info('%s has been packed to %s' % \
                          (zip_dirname, zip_filename))
        except subprocess.CalledProcessError as cpe:
            logging.error('failed on packing %s.\n %s'% \
                          (zip_dirname, cpe.output))
            raise SystemError("failure happen in packing process.")
            
        
    def _removeit(self, dirname):
        try:
            if self.__dircheck(dirname) == True:
                shutil.rmtree(dirname)
        except Exception as err:
            logging.exception('removing %s failed.' % dirname)
            
    def __dircheck(self, dirname):
        if sys.platform == 'win32':
            path = os.path.splitdrive(dirname)[1]
            path = os.path.normpath(path)
            path = path.lstrip(os.sep)
            pathcomps = path.split(os.sep)
            if (pathcomps[0].lower() != 'builds') and \
               ((pathcomps[1].lower() != 'applications') or \
                (pathcomps[1].lower() != 'components')):
                logging.error("%s should not be touched."\
                              % dirname)
                return False
            if (pathcomps[3].lower() != 'auto'):
                logging.error("Only the data under auto directory can be touched.")
                return False
            return True
        return False
    
    def archiveit(self):
        if not os.path.isdir(self.dirname):
            logging.warn("%s is not a directory." % self.dirname)
            return
        dirs_under_auto = os.listdir(self.dirname)
        for dir_under_auto in dirs_under_auto:
            if not os.path.isdir(os.path.join(self.dirname, dir_under_auto)):
                if os.path.splitext(dir_under_auto)[1].lower() == '.zip':
                    continue
                else:
                    logging.warn('%s is not an archive file.'% 
                                 os.path.join(self.dirname, dir_under_auto))
                    continue
            if dir_under_auto.lower().find('latest') != -1:
                continue
            try:
                if not dir_under_auto[-6:].isdigit():
                    logging.warn("%s is not in normal structure!" % 
                                 os.path.join(self.dirname, dir_under_auto))
                    continue
            except Exception:
                logging.warn("%s is not in normal structure!" % 
                             os.path.join(self.dirname, dir_under_auto))
                continue
                
            fulldir_under_auto = os.path.join(self.dirname, dir_under_auto)
            if os.path.isdir(fulldir_under_auto):
                if self._olderthan(fulldir_under_auto, 90):
                    try:
                        self._packit(fulldir_under_auto, dir_under_auto)
                        self._removeit(fulldir_under_auto)
                    except Exception:
                        logging.error('problem happened in archiving %s !' %
                                      os.path.join(self.dirname, dir_under_auto))
    
    def _olderthan(self, dirname, day=None):
        """
        on windows, os.path.getmtime get the timestamp from epoch of 
        modification, we use modification time not creation time.
        """
        if day == None:
            return False
        if sys.platform == 'win32':
            datedelta = datetime.timedelta(day)
            olddatethreshold = datetime.date.today() - datedelta
            try:
                mtimestamp = os.path.getmtime(dirname)
                mdate = datetime.date.fromtimestamp(mtimestamp)
                if mdate < olddatethreshold:
                    logging.info('%s is older than %d days.' % (dirname, day)) 
                    return True
                logging.debug('%s is NOT old than %d days.' % (dirname, day))
                return False
            except os.error:
                logging.error('failed on getting mtime of %s.' % (dirname))
                return False
        return False
    
    @property
    def dirname(self):
        return self._dirname
    
    @dirname.setter
    def dirname(self, dirname):
        if (dirname == None) or (not isinstance(dirname, str)):
            logging.error('"dirname" argument is not satisfied the conditions!')
            raise WrongArgument
            
        if sys.platform == 'win32':
            if dirname[1] != ':':
                logging.error('The directory name must be absolute path name.')
                raise SystemError('The directory name must be absolute path name.')
            if self.__dircheck(dirname) == True:
                self._dirname = dirname
        elif sys.platform == 'linux2':
            if dirname[0] != os.sep:
                logging.error('The directory name must be absolute path name.')
                raise SystemError('The directory name must be absolute path name.')
        else:
            raise NotImplementedError()

def archive_build_releases():
    comp_dir = r''
    app_dir = r''
    archiver = ArchiveDeliveryDirectory()

    if comp_dir.strip() != r'':
        comps = os.listdir(comp_dir)
        for comp in comps:
            archiver.dirname = os.path.join(comp_dir, comp, 'Auto')
            archiver.archiveit()
        
    if app_dir.strip() != r'':
        apps = os.listdir(app_dir)        
        for app in apps:
            archiver.dirname = os.path.join(app_dir, app, 'Auto')
            archiver.archiveit()

if __name__ == '__main__':
    # create file handler which logs even debug messages
    fh = logging.FileHandler('ai.log')
    fh.setLevel(logging.WARNING)
    fh_info = logging.FileHandler('ai_debug.log',mode='w')
    fh_info.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    fh_info.setFormatter(formatter)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(ch)
    logging.getLogger().addHandler(fh)
    logging.getLogger().addHandler(fh_info)
    archive_build_releases()
