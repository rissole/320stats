import os
import facebook
import json
import re
from flask import *
from jinja2 import evalcontextfilter, Markup, escape
from member import Member
from group import Group
from apscheduler.scheduler import Scheduler

### APP SETUP ###

# Start the scheduler
sched = Scheduler()
sched.start()

# Prepare Flask
app = Flask(__name__)

# Prepare Facebook
oauth = ''
with open('oauth') as f:
	oauth = f.read()
GRAPH = facebook.GraphAPI(oauth)

## should we do the slow process of getting who likes each comment?
GET_LIKERS = False

## Group IDs
GROUPS = {'320':'155001391342630', '420':'400112543380892', 'tvcjc':'212009085616947'}
g320 = Group(GROUPS['320'])

#################

def downloadGroupJSON(groupID):
    kwargs = {
        'limit': 1000,
        'fields': 'comments.limit(500),created_time,from,full_picture,description,icon,id,link,message,message_tags,name,object_id,picture,caption,source,status_type,type,updated_time,with_tags,likes,actions'
    }
    total_feed = {'data': []}
    while True:
        feed = GRAPH.get_object(groupID+'/feed', **kwargs)
        if feed['data']:
            total_feed['data'] += feed['data']
            until = re.search(r'until=(\d+)', feed['paging']['next']).group(1)
            #print "until:", until
            kwargs['until'] = until
            kwargs['offset'] = 1
        else:
            break
            
    with open(groupID+'_feed.json', 'w') as f:
        f.write(json.dumps(total_feed))
        
def get_likers_for_comment(post_id, comment_id):
	if GET_LIKERS == False:
		return []
	else:
		print('getting liker data')
		likers_data = GRAPH.get_object(post_id+'_'+comment_id+'/likes', fields='name')
		likers = [ l['name'] for l in likers_data['data'] ]
		return likers

def get_lastcheck():
    # "a+" => open file for reading and writing, does not truncate
    f = open('lastcheck', 'a+')
    lastcheck = f.read()
    f.close()
    if (lastcheck != ''):
        lastcheck = float(lastcheck)
    print 'Checking... lastcheck=' + str(lastcheck)
    return lastcheck
    
def populate_data(group):
    with open(group.get_gid()+'_feed.json', 'r') as f:
        jjson = f.read()
    d = json.loads(jjson)
    
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
        
@app.template_filter('nicenum')
def nice_num_filter(n):
    return '{:,}'.format(n)

@app.route('/')
def root():
    stats = {}
    for stat in Group.stats.keys():
        stats[stat] = g320.get_stat(stat)
    return render_template('group.htm', stats=stats, members=g320.get_member_names())
    
@app.route('/m/<name>')
def member(name):
    m = g320.get_member(name)
    if m == None:
        return render_template('error.htm', error={'title': 'Member not found', 'message': 'That member doesn\'t exist, dude.'})
    stats = {}
    for stat in Member.stats.keys():
        stats[stat] = m.get_stat(stat)
    
    return render_template('member.htm', stats=stats, uid=m.get_uid(), name=m.get_name(), members=g320.get_member_names())

def update_cache(group):
    downloadGroupJSON(group.get_gid())
    populate_data(g320)
    
if __name__ == '__main__':
    try:
        with open(g320.get_gid()+'_feed.json'):
            pass
    except IOError:
        downloadGroupJSON(g320.get_gid())
    finally:
        populate_data(g320)
        
    sched.add_interval_job(lambda: update_cache(g320), days=1)
    
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)#, use_reloader=False)
