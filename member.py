import wordcloud

class Member:
    
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

    def __init__(self, name, uid, group):
        self._name = name
        self._uid = uid
        self._group = group
        self._posts = []
        self._comments = []
        self._liked_posts = []
        self._stats = {}
        
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
        
    def get_group(self):
        return self._group
        
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
    
    def get_stat(self, stat_key):
        return self._stats.get(stat_key)
    
    # STATS CALCS #
    # NUM_POSTS
    def calc_num_posts(self):
        self._stats['NUM_POSTS'] = len(self._posts)
        
    # NUM_COMMENTS
    def calc_num_comments(self):
        self._stats['NUM_COMMENTS'] = len(self._comments)
        
    # NUM_LIKED_POSTS
    def calc_num_liked_posts(self):
        self._stats['NUM_LIKED_POSTS'] = len(self._liked_posts)
    
    # POST_LIKES_RECEIVED
    def calc_post_likes_received(self):      
        likes = 0
        for post in self._posts:
            if 'likes' in post:
                likes += len(post['likes']['data'])
        
        self._stats['POST_LIKES_RECEIVED'] = likes
        
    # COMMENT_LIKES_RECEIVED
    def calc_comment_likes_received(self):
        likes = 0
        for comment in self._comments:
            likes += comment['like_count']
        
        self._stats['COMMENT_LIKES_RECEIVED'] = likes
        
    # WHO_LIKED_MY_POSTS
    def calc_who_liked_posts(self):
        likes = {}
        for name in self._group.get_member_names():
            likes[name] = 0
            
        for post in self._posts:
            if 'likes' in post:
                for like in post['likes']['data']:
                    likes[like['name']] += 1
        
        self._stats['WHO_LIKED_MY_POSTS'] = likes.items()
        
    # WHOSE_POSTS_WERE_LIKED
    def calc_whose_posts_were_liked(self):
        likes = {}
        for name in self._group.get_member_names():
            likes[name] = 0
            
        for post in self._liked_posts:
            likes[post['from']['name']] += 1
        
        self._stats['WHOSE_POSTS_WERE_LIKED'] = likes.items()
        
    # IRRELEVANT_POSTS
    def calc_num_irrelevant_posts(self):
        posts = []
        for post in self._posts:
            if 'likes' in post:
                continue
            if 'comments' in post:
                continue
            posts.append({'id': post['id'], 'message': post['message'][:50]+'...' if 'message' in post else '[Image]'})
        
        self._stats['IRRELEVANT_POSTS'] = posts
        
    # AVERAGE_COMMENT_LENGTH
    def calc_average_comment_length(self):
        total_length = 0
        for comment in self._comments:
            total_length += len(comment['message'])
        
        num_comments = self.get_stat('NUM_COMMENTS')
        self._stats['AVERAGE_COMMENT_LENGTH'] = 0 if num_comments == 0 else total_length / num_comments
        
    # LONGEST_COMMENT
    def calc_longest_comment(self):
        if len(self._comments) == 0:
            self._stats['LONGEST_COMMENT'] = {'id': '0', 'message': ''}
        else:
            longest_comment = max(self._comments, key=lambda x: len(x['message']))
            self._stats['LONGEST_COMMENT'] = {'id': longest_comment['id'], 'message': longest_comment['message']}
        
    # MOST_COMMON_WORDS
    def calc_most_common_words(self):
        text = ' '.join(c['message'] for c in self._comments).lower()
        self._stats['MOST_COMMON_WORDS'] = wordcloud.get_top_words(text)
        
    # BLAZED_POSTS
    def calc_blazed_posts(self):
        members_set = set(self._group.get_member_names())
        posts = []
        for post in self._posts:
            if 'likes' in post:
                poster = post['from']['name']
                blazed_members_set = members_set.copy()
                blazed_members_set.discard(poster)
                if len(blazed_members_set - set(m['name'] for m in post['likes']['data'])) == 0:
                    posts.append({'id': post['id'], 'message': post['message'][:50]+'...' if 'message' in post else '[Image]'})
                    
        self._stats['BLAZED_POSTS'] = posts