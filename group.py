from member import Member

class Group:

    # stat enum, keys of this dict are valid keys for _stats
    stats = {
        'NUM_POSTS': 'Posts',
        'NUM_COMMENTS': 'Comments',
        'POSTS_PER_MEMBER': 'Posts per member',
        'POST_LIKES_PER_MEMBER': 'Post likes per member',
        'COMMENTS_PER_MEMBER': 'Comments per member',
        'COMMENT_LIKES_PER_MEMBER': 'Comments per member',
    }
    
    def __init__(self, gid, name):
        self._gid = gid
        self._name = name
        self._stats = {}
        # (id, name) -> member obj
        self._members = {}
        self._member_names = []
        
    def get_gid(self):
        return self._gid
        
    def get_name(self):
        return self._name
        
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
        
    def get_stat(self, stat_key):
        return self._stats[stat_key]
        
    def get_template_vars(self):
        return {'id': self.get_gid(), 'name': self.get_name(), 'members': self.get_member_names()}
    
    # STATS CALCS #
    # NUM_POSTS
    def calc_num_posts(self):
        self._stats['NUM_POSTS'] = sum(m.get_stat('NUM_POSTS') for m in self.get_members())
        
    # NUM_COMMENTS
    def calc_num_comments(self):
        self._stats['NUM_COMMENTS'] = sum(m.get_stat('NUM_COMMENTS') for m in self.get_members())
    
    #POSTS_PER_MEMBER
    def calc_posts_per_member(self):
        self._stats['POSTS_PER_MEMBER'] = [(m.get_name(), m.get_stat('NUM_POSTS')) for m in self.get_members()]
        
    #POST_LIKES_PER_MEMBER
    def calc_post_likes_per_member(self):
        self._stats['POST_LIKES_PER_MEMBER'] = [(m.get_name(), m.get_stat('POST_LIKES_RECEIVED')) for m in self.get_members()]
        
    #COMMENTS_PER_MEMBER
    def calc_comments_per_member(self):
        self._stats['COMMENTS_PER_MEMBER'] = [(m.get_name(), m.get_stat('NUM_COMMENTS')) for m in self.get_members()]
        
    #COMMENT_LIKES_PER_MEMBER
    def calc_comment_likes_per_member(self):
        self._stats['COMMENT_LIKES_PER_MEMBER'] = [(m.get_name(), m.get_stat('COMMENT_LIKES_RECEIVED')) for m in self.get_members()]