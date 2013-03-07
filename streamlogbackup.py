import os

from datasync import DirectorySyncer
from datasync import SVNSyncer


src = r'\\fileserver\RD\QA\BugStreams'
dst = r'D:\BugStreams'

class StreamLogSyncer(SVNSyncer):
    def __init__(self):
        SVNSyncer.__init__(self)
        self.svn_dir = dst
        self.svn_url = ''
        self.svn_username = ''
        self.svn_password = ''
    
    def sync(self):
        """
        Assumed that the location on subversion server for StreamLog have been
        set up.
        1.Check if destination exists or not, it does then go to 3;
        2.Check out on the destination from svn_url;
        3.Check the status of destination, it should be clean otherwise quit;
        4.Update the destination, if goes wrong, quit;
        5.Sync the source and destination directory;
        6.check the status of destination, if there's new stream.log need added,
        added it, if adding goes wrong, quit;
        7.check in all motified and added steam.log to the subversion server.
        """
        if not os.path.exists(self.svn_dir):
            self.checkout_wc()

        if not self.status_wc():
            print 'at this time, working copy should be totally clean and ready.'
            sys.exit(-1)

        self.update_wc()
        
        dirsync = DirectorySyncer([src], [dst])
        dirsync._included.append('stream.log')
        dirsync.sync()
        
        if self.status_wc():
            return
        
        self.add_wc()
        self.checkin_wc("update the stream.log from server.")

if __name__ == "__main__":
    sls = StreamLogSyncer()
    sls.sync()