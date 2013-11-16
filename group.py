from member import Member

class Group:

    # stat enum, keys of this dict are valid keys for _stats
    stats = {
        'NUM_POSTS': 'Posts',
        'NUM_COMMENTS': 'Comments',
        'POSTS_PER_MEMBER': 'Posts per member',
    }
    
    def __init__(self, gid):
        self._gid = gid
        self._stats = {}
        # (id, name) -> member obj
        self._members = {}
        self._member_names = []
        
    def get_gid(self):
        return self._gid
        
    def make_or_get_member(self, name, uid=0):
        if name in self._members:
            return self._members[name]
        else:
            m = Member(name, uid, self)
            self._members[name] = m
            self._update_member_names()
            return m
            
    def get_member(self, name):
        return self._members.get(name)
            
    def _update_member_names(self):
        self._member_names = sorted(self._members.keys())
        
    def get_member_names(self):
        return self._member_names
        
    def get_members(self):
        return self._members.values()
        
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
        
        self._stats['NUM_POSTS'] = sum(m.get_stat('NUM_POSTS') for m in self.get_members())
        return self._stats['NUM_POSTS']
        
    # NUM_COMMENTS
    def calc_num_comments(self):
        cached = self.get_stat('NUM_COMMENTS')
        if cached != None:
            return cached
        
        self._stats['NUM_COMMENTS'] = sum(m.get_stat('NUM_COMMENTS') for m in self.get_members())
        return self._stats['NUM_COMMENTS']