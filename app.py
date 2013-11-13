import os
import facebook
import json
import re
from flask import Flask
from member import Member
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
GROUPS = {'320':'155001391342630', '420':'400112543380892'}

#################

def downloadGroupJSON(groupID):
    open(groupID+'_feed.json', 'w').close()
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
            print "until:", until
            kwargs['until'] = until
            kwargs['offset'] = 1
        else:
            break
    with open(groupID+'_feed.json', 'a') as f:
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

@app.route('/')
def root():
    return 'Hello World!'

if __name__ == '__main__':
    with open(GROUPS['320']+'_feed.json') as f:
        jjson = f.read()
    d = json.loads(jjson)
    for post in d['data']:
        poster = Member.make_or_get_member(post['from']['name'])
        poster.add_post(post)
        
        if 'comments' in post:
            comments = post['comments']['data']
            for comment in comments:
                commenter = Member.make_or_get_member(comment['from']['name'])
                commenter.add_comment(comment)
                
        if 'likes' in post:
            likes = post['likes']['data']
            for like in likes:
                liker = Member.make_or_get_member(like['name'])
                liker.add_liked_post(post)
                
    for member in Member.members.values():
        member.calc_num_posts()
        member.calc_num_comments()
        member.calc_num_liked_posts()
        member.calc_post_likes_received()
        member.calc_comment_likes_received()
        member.calc_who_liked_posts()
        member.calc_num_irrelevant_posts()
        member.calc_average_comment_length()
        member.calc_longest_comment()
        member.print_stats()
        print ''
    
    #sched.add_interval_job(poo, seconds=1)
    
    # Bind to PORT if defined, otherwise default to 5000.
    #port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port, debug=True)#, use_reloader=False)
