import json
import facebook
import re
import threading
from group import Group

# gid -> group obj
_groups = {}

# gid -> {'result': [downloading|complete|error], 'error': error string}
_download_status = {}

# websockets that are open
_sockets = []

def get_group(gid):
    # todo: check lastcheck < 1 day or whatever
    return _groups.get(gid, False)
    
def add_group(group):
    _groups[group.get_gid()] = group
    
def fetch_groups_for_user(oauth):
    try:
        graph = facebook.GraphAPI(oauth)
        groups = graph.get_object('/me/groups', fields='id')
        if 'error' in groups or not groups['data']:
            return []
        return [ g['id'] for g in groups['data'] ]
    except GraphAPIError:
        return []

def downloadGroupJSON(groupID, oauth):
    graph = facebook.GraphAPI(oauth)
    
    kwargs = {
        'limit': 1000,
        'fields': 'comments.limit(500),created_time,from,full_picture,description,icon,id,link,message,message_tags,name,object_id,picture,caption,source,status_type,type,updated_time,with_tags,likes,actions'
    }
    name = graph.get_object(groupID, fields="name")['name']
    total_feed = {'data': [], 'name': name}
    
    while True:
        feed = graph.get_object(groupID+'/feed', **kwargs)
        if feed['data']:
            total_feed['data'] += feed['data']
            until = re.search(r'until=(\d+)', feed['paging']['next']).group(1)
            #print "until:", until
            kwargs['until'] = until
            kwargs['offset'] = 1
        else:
            break
            
    with open(groupID+'.json', 'w') as f:
        f.write(json.dumps(total_feed))
    return total_feed
    
def populate_data(group, d):  
    for post in d['data']:
        poster = group.make_or_get_member(post['from']['name'], post['from']['id'])
        poster.add_post(post)
        
        if 'comments' in post:
            comments = post['comments']['data']
            for comment in comments:
                commenter = group.make_or_get_member(comment['from']['name'], comment['from']['id'])
                commenter.add_comment(comment)
                
        if 'likes' in post:
            likes = post['likes']['data']
            for like in likes:
                liker = group.make_or_get_member(like['name'], like['id'])
                liker.add_liked_post(post)
                
    for member in group.get_members():
        member.calc_num_posts()
        member.calc_num_comments()
        member.calc_num_liked_posts()
        member.calc_post_likes_received()
        member.calc_comment_likes_received()
        member.calc_who_liked_posts()
        member.calc_num_irrelevant_posts()
        member.calc_average_comment_length()
        member.calc_longest_comment()
        member.calc_most_common_words()
        member.calc_whose_posts_were_liked()
        member.calc_blazed_posts()
        
    # group wide stuff is calculated off member stuff, so must be
    # after member stuff.
    group.calc_num_posts()
    group.calc_num_comments()
    group.calc_posts_per_member()
    group.calc_post_likes_per_member()
    group.calc_comments_per_member()
    group.calc_comment_likes_per_member()
    
def register_socket(ws):
    _sockets.append(ws)
    
def get_download_status(gid):
    return _download_status.get(gid)
    
def start_group_download(gid, oauth):
    _download_status[gid] = {'result': 'downloading'}
    t = threading.Thread(target=download_group_thread, args = (gid, oauth))
    t.start()
    
def download_group_thread(gid, oauth):
    global _sockets
    try:
        print "getting group",gid
        feed = downloadGroupJSON(gid, oauth)
        group = Group(gid, feed['name'])
        populate_data(group, feed)
        add_group(group)
        _download_status[gid] = {'result': 'complete'}
        print "Got group",gid
    except facebook.GraphAPIError as e:
        print "failed getting group",gid,":",e.message
        _download_status[gid] = {'result': 'error', 'error': e.message}
        
    for ws in _sockets:
        if ws is not None:
            ws.send(gid)
    _sockets = filter(lambda ws: ws is not None, _sockets)
