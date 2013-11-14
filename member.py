import wordcloud

class Member:
    # {name -> class obj} of existing members
    members = {}
    
    # stat enum, keys of this dict are valid keys for _stats
    stats = {
        'NUM_POSTS': 'Posts',
        'NUM_COMMENTS': 'Comments',
        'NUM_LIKED_POSTS': 'Posts likes given',
        'WHOSE_POSTS_WERE_LIKED': 'Whose posts were liked',
        'POST_LIKES_RECEIVED': 'Post likes received',
        'COMMENT_LIKES_RECEIVED': 'Comment likes received',
        'WHO_LIKED_MY_POSTS': 'Users who liked my posts',
        'IRRELEVANT_POSTS': 'Irrelevant posts',
        'AVERAGE_COMMENT_LENGTH': 'Average comment length (chars)',
        'LONGEST_COMMENT': 'Longest comment',
        'MOST_COMMON_WORDS': 'Most common words',
        'BLAZED_POSTS': 'Posts that were liked by all',
    }
    
    @classmethod
    def make_or_get_member(self, name, uid=0):
        if name in Member.members:
            return Member.members[name]
        else:
            return Member(name, uid)
    
    def __init__(self, name, uid):
        self._name = name
        self._uid = uid
        self._posts = []
        self._comments = []
        self._liked_posts = []
        self._stats = {}
        Member.members[name] = self
        
    def add_post(self, p):
        self._posts.append(p)
    
    def add_comment(self, c):
        self._comments.append(c)
        
    def add_liked_post(self, p):
        self._liked_posts.append(p)
        
    def get_name(self):
        return self._name
        
    def get_uid(self):
        return self._uid
        
    def get_posts(self):
        return self._posts
    
    def get_comments(self):
        return self._comments
        
    def get_liked_posts(self):
        return self._liked_posts
        
    def print_stats(self):
        print self.get_name() + ':'
        for stat_key, stat in Member.stats.items():
            print stat + ':', self.get_stat(stat_key)
    
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
        
    # NUM_LIKED_POSTS
    def calc_num_liked_posts(self):
        cached = self.get_stat('NUM_LIKED_POSTS')
        if cached != None:
            return cached
        
        self._stats['NUM_LIKED_POSTS'] = len(self._liked_posts)
        return self._stats['NUM_LIKED_POSTS']
    
    # POST_LIKES_RECEIVED
    def calc_post_likes_received(self):
        cached = self.get_stat('POST_LIKES_RECEIVED')
        if cached != None:
            return cached
        
        likes = 0
        for post in self._posts:
            if 'likes' in post:
                likes += len(post['likes']['data'])
        
        self._stats['POST_LIKES_RECEIVED'] = likes
        return self._stats['POST_LIKES_RECEIVED']
        
    # COMMENT_LIKES_RECEIVED
    def calc_comment_likes_received(self):
        cached = self.get_stat('COMMENT_LIKES_RECEIVED')
        if cached != None:
            return cached
        
        likes = 0
        for comment in self._comments:
            likes += comment['like_count']
        
        self._stats['COMMENT_LIKES_RECEIVED'] = likes
        return self._stats['COMMENT_LIKES_RECEIVED']
        
    # WHO_LIKED_MY_POSTS
    def calc_who_liked_posts(self):
        cached = self.get_stat('WHO_LIKED_MY_POSTS')
        if cached != None:
            return cached
        
        likes = {}
        for name in Member.members.keys():
            likes[name] = 0
            
        for post in self._posts:
            if 'likes' in post:
                for like in post['likes']['data']:
                    likes[like['name']] += 1
        
        likes = [(x[0], x[1]) for x in likes.iteritems()]
        self._stats['WHO_LIKED_MY_POSTS'] = likes
        return self._stats['WHO_LIKED_MY_POSTS']
        
    # WHOSE_POSTS_WERE_LIKED
    def calc_whose_posts_were_liked(self):
        cached = self.get_stat('WHOSE_POSTS_WERE_LIKED')
        if cached != None:
            return cached
        
        likes = {}
        for name in Member.members.keys():
            likes[name] = 0
            
        for post in self._liked_posts:
            likes[post['from']['name']] += 1
        
        likes = [(x[0], x[1]) for x in likes.iteritems()]
        self._stats['WHOSE_POSTS_WERE_LIKED'] = likes
        return self._stats['WHOSE_POSTS_WERE_LIKED']
        
    # IRRELEVANT_POSTS
    def calc_num_irrelevant_posts(self):
        cached = self.get_stat('IRRELEVANT_POSTS')
        if cached != None:
            return cached
        
        posts = []
        for post in self._posts:
            if 'likes' in post:
                continue
            if 'comments' in post:
                continue
            posts.append(post['id'])
        
        self._stats['IRRELEVANT_POSTS'] = posts
        return self._stats['IRRELEVANT_POSTS']
        
    # AVERAGE_COMMENT_LENGTH
    def calc_average_comment_length(self):
        cached = self.get_stat('AVERAGE_COMMENT_LENGTH')
        if cached != None:
            return cached
        
        total_length = 0
        for comment in self._comments:
            total_length += len(comment['message'])
        
        self._stats['AVERAGE_COMMENT_LENGTH'] = total_length / self.get_stat('NUM_COMMENTS')
        return self._stats['AVERAGE_COMMENT_LENGTH']
        
    # LONGEST_COMMENT
    def calc_longest_comment(self):
        cached = self.get_stat('LONGEST_COMMENT')
        if cached != None:
            return cached
        
        longest_comment = max(self._comments, key=lambda x: len(x['message']))
        
        self._stats['LONGEST_COMMENT'] = {'id': longest_comment['id'], 'message': longest_comment['message']}
        return self._stats['LONGEST_COMMENT']
        
    # MOST_COMMON_WORDS
    def calc_most_common_words(self):
        cached = self.get_stat('MOST_COMMON_WORDS')
        if cached != None:
            return cached
            
        text = ' '.join(c['message'] for c in self._comments).lower()
        self._stats['MOST_COMMON_WORDS'] = wordcloud.get_top_words(text)
        return self._stats['MOST_COMMON_WORDS']
        
    # BLAZED_POSTS
    def calc_blazed_posts(self):
        cached = self.get_stat('BLAZED_POSTS')
        if cached != None:
            return cached
        
        members_set = set(Member.members.keys())
        posts = []
        for post in self._posts:
            if 'likes' in post:
                poster = post['from']['name']
                blazed_members_set = members_set.copy()
                blazed_members_set.discard(poster)
                if len(blazed_members_set - set(m['name'] for m in post['likes']['data'])) == 0:
                    posts.append({'id': post['id'], 'message': post['message'][:50]+'...' if 'message' in post else '[Image]'})
                    
        self._stats['BLAZED_POSTS'] = posts
        return self._stats['BLAZED_POSTS']