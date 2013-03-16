# -*- coding: utf-8 -*-
import filecmp
import os
import shutil
import subprocess
import sys

class NotSupportedTypeArgumentError(Exception): pass
class NotSVNSupportInShell(Exception): pass

class DataSync(object):
    def __init__(self, source=None, dest=None):
        """
        source and dest must be list type.
        """
        if source == None:
            self._source_list = []
        else:
            self._source_list = source
        if dest == None:
            self._dest_list = []
        else:
            self._dest_list = dest
    
    def add_source(self, src):
        if isinstance(src, str):
            if src not in self._source_list:
                self._source_list.append(src)
                return
        if isinstance(src, list):
            for item in src:
                if src not in self._source_list:
                    self._source_list.append(src)
            return
        raise NotSupportedTypeArgumentError
    
    def add_destination(self, dest):
        if isinstance(dest, str):
            if dest not in self._dest_list:
                self._dest_list.append(src)
                return
        if isinstance(dest, list):
            for item in dest:
                if dest not in self._dest_list:
                    self._dest_list.append(src)
            return
        raise NotSupportedTypeArgumentError

    def sync():
        raise NotImplementedError
    
    
class DirectorySyncer(DataSync):
    def __init__(self, source=None, dest=None):
        DataSync.__init__(self, source, dest)
        self._excluded = []
        self._included = []
        self._depth = 1
    
    def sync(self):
        """
        1.get the path list under source directory root
        2.if _included is not empty, just backup the files in _included list
        3.if _included is empty, copy all files in directory except the files in _excluded list
        4.use the _depth to control which level directory will be considered.
        """
        if (len(self._source_list) == 0) or (len(self._dest_list) == 0):
            return
        
        for src in self._source_list:
            self._sync('.', src, self._depth)
    
    def _sync(self, parent_path, src, depth):
        
        def processfile(parent_path, path, src, dest_list):
            for dest in dest_list:
                if not os.path.exists(''.join([
                    dest.rstrip(os.sep),
                    os.sep,
                    parent_path
                    ])):
                    try:
                        os.makedirs(''.join([
                            dest.rstrip(os.sep),
                            os.sep,
                            parent_path
                        ]))
                    except Exception:
                        print "failed on mkdir %s" % ''.join([
                            dest.rstrip(os.sep),
                            os.sep,
                            parent_path
                            ])
                        sys.exit(-1)
                srcfile = ''.join([
                    src.rstrip(os.sep),
                    os.sep,
                    parent_path,
                    os.sep,
                    path])
                dstfile = ''.join([
                    dest.rstrip(os.sep),
                    os.sep,
                    parent_path,
                    os.sep,
                    path])

                if os.path.exists(dstfile):
                    if filecmp.cmp(srcfile, dstfile):
                        continue
                shutil.copy2(srcfile, dstfile)
            
        if depth < 0:
            return
        else:
            depth -= 1
        
        paths = os.listdir(''.join([src.rstrip(os.sep), os.sep, parent_path]))
        
        for path in paths:
            if os.path.isdir(''.join([
                src.rstrip(os.sep), 
                os.sep, 
                parent_path, 
                os.sep, 
                path])):
                self._sync(''.join([parent_path, os.sep, path]), src, depth)
                continue
            
            if not (len(self._included) == 0):
                if path not in self._included:
                    continue
                processfile(parent_path, path, src, self._dest_list)
                continue
            
            if path in self._excluded:
                continue
            
            processfile(parent_path, path, src, self._dest_list)          
    
    def set_source(self, src_path):
        self.add_source([src_path])
    
    def set_destination(self, dst_path):
        self.add_destination([dst_path])
    
    
class SVNSyncer(DataSync):
    _SVN_CMD_ADD = 'add'
    _SVN_CMD_CI = 'ci'
    _SVN_CMD_CO = 'co'
    _SVN_CMD_STATUS = 'status'
    _SVN_CMD_UPDATE = 'update'
    _SVN_DEFAULT_OPTION = ' --no-auth-cache --username %s --password %s '
    
    def __init__(self):
        
        def checksvn():
            if os.system('svn --quiet --version') != 0:
                raise NotSVNSupportInShell()
        try:
            checksvn()
        except NotSVNSupportInShell:
            print "check the 'svn' support in your current shell!"
            sys.exit(-1)
        self._svn = 'svn'
        self._username = ''
        self._svnurl = ''
        self._svndir = ''
        self._password = ''
        self._addlist = []
        
      
    def sync(self):
        raise NotImplementedError
    
    def update_wc(self):
        error_str = 'Skipped'
        cmdlist = []
        cmdlist.append(self._svn)
        options = self._SVN_DEFAULT_OPTION % ( self.svn_username, self._password)
        options = options.split()
        for option in options:
            cmdlist.append(option)
        cmdlist.append(self._SVN_CMD_UPDATE)
        cmdlist.append(self.svn_dir)
        failed = False
        try:
            retstr = subprocess.check_output(cmdlist, shell=True)
            if retstr.find(error_str) != -1:
                failed = True
        except subprocess.CalledProcessError as err:
            failed = True
            print err
        finally:
            if failed:
                print 'update %s :failed!' % self.svn_dir
                print ' svn sync will not continue, script exit.'
                sys.exit(-1)
        
    def status_wc(self):
        error_str = 'is not a working copy'
        cmdlist = []
        cmdlist.append(self._svn)
        cmdlist.append(self._SVN_CMD_STATUS)
        cmdlist.append(self.svn_dir)
        failed = False
        try:
            retstr = subprocess.check_output(cmdlist, shell=True)
            if retstr.find(error_str) != -1:
                failed = True
            if len(retstr) == 0:
                return True
            lines = retstr.split(os.linesep)
            for line in lines:
                if line.strip() == '':
                    continue
                if line[0] == '?':
                    self._addlist.append(line.split()[1].strip()) 
            return False
        except subprocess.CalledProcessError as err:
            failed = True
            print err
        finally:
            if failed:
                print 'status %s :failed!' % self.svn_dir
                print ' svn sync will not continue, script exit.'
                sys.exit(-1)


 
    def checkin_wc(self, msg):
        cmdlist = []
        cmdlist.append(self._svn)
        options = self._SVN_DEFAULT_OPTION % ( self.svn_username, self._password)
        options = options.split()
        for option in options:
            cmdlist.append(option)
        cmdlist.append(self._SVN_CMD_CI)
        cmdlist.append('-m')
        cmdlist.append('"%s"'% msg)
        cmdlist.append(self.svn_dir)
        failed = False
        try:
            retstr = subprocess.check_output(cmdlist, shell=True)
        except subprocess.CalledProcessError as err:
            failed = True
            print err
        finally:
            if failed:
                print 'checkin %s :failed!' % self.svn_dir
                print ' svn sync will not continue, script exit.'
                sys.exit(-1)
        
    def checkout_wc(self):
        cmdlist = []
        cmdlist.append(self._svn)
        options = self._SVN_DEFAULT_OPTION % ( self.svn_username, self._password)
        options = options.split()
        for option in options:
            cmdlist.append(option)
        cmdlist.append(self._SVN_CMD_CO)
        cmdlist.append('%s' % self._svnurl)
        cmdlist.append(self.svn_dir)
        failed = False
        try:
            retstr = subprocess.check_output(cmdlist, shell=True)
        except subprocess.CalledProcessError as err:
            failed = True
            print err
        finally:
            if failed:
                print 'checkout %s :failed!' % self.svn_dir
                print ' svn sync will not continue, script exit.'
                sys.exit(-1)
    
    def add_wc(self):
        if len(self._addlist) == 0:
            return
        cmdlist = []
        cmdlist.append(self._svn)
        cmdlist.append(self._SVN_CMD_ADD)
        for item in self._addlist:
            cmdlist.append("%s" % item)
        failed = False
        try:
            retstr = subprocess.check_output(cmdlist, shell=True)
        except subprocess.CalledProcessError as err:
            failed = True
            print err
        finally:
            if failed:
                print 'adding file failed.'
                print ' svn sync will not continue, script exit.'
                sys.exit(-1)
            
    @property
    def svn_dir(self):
        return self._svndir
    
    @svn_dir.setter
    def svn_dir(self, path):
        self._svndir = path
    
    @property
    def svn_username(self):
        return self._username
    
    @svn_username.setter
    def svn_username(self, name):
        self._username = name
        
    @property
    def svn_password(self):
        pass
    
    @svn_password.setter
    def svn_password(self, password):
        self._password = password
        
    
    @property
    def svn_url(self):
        return self._svnurl
    
    @svn_url.setter
    def svn_url(self, url):
        self._svnurl = url
    
    
    
    
if __name__ == "__main__":
    pass
