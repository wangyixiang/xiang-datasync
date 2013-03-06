# -*- coding: utf-8 -*-
import os
import sys
import shutil
import filecmp

class NotSupportedTypeArgumentError(Exception): pass

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
    

class StreamLogSyncer:
    def __init__(self):
        pass
    
    def sync(self):
        pass
    
    def set_source(self, src_path):
        pass
    
    def set_destination(self, dst_path):
        pass
    
    
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
                for dest in self._dest_list:
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
                continue
            
            if path in self._excluded:
                continue
            
            for dest in self._dest_list:
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
                dstfile = ''.join([
                    dest.rstrip(os.sep),
                    os.sep,
                    parent_path,
                    os.sep,
                    path])
                srcfile = ''.join([
                    src.rstrip(os.sep),
                    os.sep,
                    parent_path,
                    os.sep,
                    path])
                
                if filecmp.cmp(dstfile, srcfile):
                    continue
                shutil.copy2(srcfile, dstfile)            
        
        
        
    
    def set_source(self, src_path):
        self.add_source([src_path])
    
    def set_destination(self, dst_path):
        self.add_destination([dst_path])
    
if __name__ == "__main__":
    dirsync = DirectorySyncer([r'\\fileserver\RD\QA\BugStreams'], [r'D:\BugStreams'])
    dirsync._included.append('stream.log')
    dirsync.sync()