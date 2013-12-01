import os
import facebook
import groupledata
import random
import re
import gevent
from flask import *
from flask_sockets import Sockets
from jinja2 import evalcontextfilter, Markup, escape
from member import Member
from group import Group

### APP SETUP ###

# Prepare Flask
app = Flask(__name__)
sockets = Sockets(app)

# Grouple App ID/Secret
GROUPLE_APP_ID = '1394394197467118'
with open('appsecret') as f:
    GROUPLE_APP_SECRET = f.read()
    
# Flask cookie secret
with open('cookiesecret') as f:
    app.secret_key = f.read()
    
loading_messages = [
    "Why not check out my friend's cool site <a href='http://textfac.es/'>textfac.es?</a>",
]

#################
        
@app.template_filter('nicenum')
def nice_num_filter(n):
    return '{:,}'.format(n)
    
def render_no_permission_error():
    return render_template('error.htm', no_nav=True, error={'title': 'Nah mate', 'message': 'You actually don\'t have permissions to view that group. Or maybe your cookie\'s expired. Just go home and start again.'})
    
def render_invalid_gid_error():
    return render_template('error.htm', no_nav=True, error={'title': 'You having a giggle?', 'message': 'That\'s not a valid Facebook group ID.'})
    
def current_user():
    if 'user' in session:
        return session['user']

    cookie = facebook.get_user_from_cookie(request.cookies, GROUPLE_APP_ID, GROUPLE_APP_SECRET)
    if cookie:
        session['user'] = {'access_token': cookie['access_token'], 'groups': groupledata.fetch_groups_for_user(cookie['access_token'])}
        return session['user']
        
    return None
    
def can_user_see_group(groupID, user):
    return (groupID in user['groups'])
    
def check_user_expired():
    try:
        facebook.GraphAPI(session['user']['access_token']).get_object('/me', fields='id')
    except facebook.GraphAPIError as e:
        if e.message.startswith('Error validating access token: Session has expired'):
            del session['user']
            
def valid_gid(gid):
    return (re.match(r'^\d+$', gid) is not None)
    
@app.route('/')
def root():
    return render_template('index.htm')
    
@app.route('/<gid>/')
def grouppage(gid):
    if not valid_gid(gid):
        return render_invalid_gid_error()
        
    user = current_user()
    if not user or not can_user_see_group(gid, user):
        return render_no_permission_error()
    
    group = groupledata.get_group(gid)
    
    if group == False:
        return download_group(gid)

    stats = {}
    for stat in Group.stats.keys():
        stats[stat] = group.get_stat(stat)
        
    return render_template('group.htm', group=group.get_template_vars(), stats=stats)
    
def download_group(gid):
    if not valid_gid(gid):
        return render_invalid_gid_error()
        
    check_user_expired()
    user = current_user()
    if not user or not can_user_see_group(gid, user):
        return render_no_permission_error()
        
    status = groupledata.get_download_status(gid)
    if status and status['result'] == 'downloading':
        return render_template('loading.htm', no_nav=True, gid=gid, title='It\'s not TIME yet...', message=random.choice(loading_messages))
    elif status and status['result'] == 'error':
        if status['error'] == 'An unknown error occurred':
            return render_template('error.htm', no_nav=True, error={'title': 'Oh jeez...', 'message': 'That group was too big for this little webapp to handle, try a different group.'})
        return render_template('error.htm', no_nav=True, error={'title': 'Oh jeez...', 'message': u'Something went wrong \xaf\\_(\uFF82)_/\xaf'})
    else:
        groupledata.start_group_download(gid, user['access_token'])
        return render_template('loading.htm', no_nav=True, gid=gid, title='I\'m on it!', message=random.choice(loading_messages))
    
@app.route('/<gid>/<name>')
def member(gid, name):
    if not valid_gid(gid):
        return render_invalid_gid_error()
        
    user = current_user()
    if not user or not can_user_see_group(gid, user):
        return render_no_permission_error()
        
    group = groupledata.get_group(gid)
    
    if group == False:
        return download_group(gid)
        
    m = group.get_member(name)
    if m == None:
        return render_template('error.htm', group=group.get_template_vars(), error={'title': 'Member not found', 'message': 'That member doesn\'t exist, dude.'})
        
    stats = {}
    for stat in Member.stats.keys():
        stats[stat] = m.get_stat(stat)
    
    return render_template('member.htm', group=group.get_template_vars(), stats=stats, uid=m.get_uid(), name=m.get_name())
    
@sockets.route('/bytes')
def refresher_socket(ws):
    groupledata.register_socket(ws)

    while ws is not None:
        gevent.sleep()

    print "closed socket"
