class Group:

    # stat enum, keys of this dict are valid keys for _stats
    stats = {
        'NUM_POSTS': 'Posts',
        'NUM_COMMENTS': 'Comments',
    }
    
    def __init__(self, gid):
        self._gid = gid
        self._posts = []
        self._comments = []
        self._stats = {}
        
    def get_gid(self):
        return self._gid
        
    def add_post(self, p):
        self._posts.append(p)
    
    def add_comment(self, c):
        self._comments.append(c)
        
    # returns None if stat not set
    def get_stat(self, stat_key):
        return self._stats.get(stat_key)
        
    # forces the stat to be recalculated next time it's requested
    def purge_stat(self, stat_key):
        self._stats.pop(stat_key, None)
    
    # STATS CALCS #
    # NUM_POSTS
    def calc_num_posts(self):
        cached = self.get_stat('NUM_POSTS')
        if cached != None:
            return cached
        
        self._stats['NUM_POSTS'] = len(self._posts)
        return self._stats['NUM_POSTS']
        
    # NUM_COMMENTS
    def calc_num_comments(self):
        cached = self.get_stat('NUM_COMMENTS')
        if cached != None:
            return cached
        
        self._stats['NUM_COMMENTS'] = len(self._comments)
        return self._stats['NUM_COMMENTS']