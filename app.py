import os
import facebook
import groupledata
from flask import *
from jinja2 import evalcontextfilter, Markup, escape
from member import Member
from group import Group

### APP SETUP ###

# Prepare Flask
app = Flask(__name__)

# Grouple App ID/Secret
GROUPLE_APP_ID = '1394394197467118'
with open('appsecret') as f:
    GROUPLE_APP_SECRET = f.read()
    
# Flask cookie secret
with open('cookiesecret') as f:
    app.secret_key = f.read()

#################
        
@app.template_filter('nicenum')
def nice_num_filter(n):
    return '{:,}'.format(n)
    
def render_no_permission_error():
    return render_template('error.htm', no_nav=True, error={'title': 'Nah mate', 'message': 'You actually don\'t have permissions to view that group. Or maybe your cookie\'s expired. Just go home and start again.'})
    
def current_user(session):
    if 'user' in session:
        return session['user']

    cookie = facebook.get_user_from_cookie(request.cookies, GROUPLE_APP_ID, GROUPLE_APP_SECRET)
    if cookie:
        session['user'] = {'access_token': cookie['access_token'], 'groups': groupledata.fetch_groups_for_user(cookie['access_token'])}
        return session['user']
        
    return None
    
def can_user_see_group(groupID, user):
    return (groupID in user['groups'])
    
@app.route('/')
def root():
    return render_template('index.htm')
    
@app.route('/<gid>/')
def grouppage(gid):
    user = current_user(session)
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
    status = groupledata.get_download_status(gid)
    downloading_message = 'We\'re crunching the numbers for your group as you read this sentence. Refresh the page after a while to see if we\'re ready.'
    if status and status['result'] == 'downloading':
        return render_template('error.htm', no_nav=True, error={'title': 'It\'s not TIME yet...', 'message': downloading_message})
    elif status and status['result'] == 'error':
        if status['error'] == 'An unknown error occurred':
            return render_template('error.htm', no_nav=True, error={'title': 'Oh jeez...', 'message': 'That group was too big for this little webapp to handle, try a different group.'})
        return render_template('error.htm', no_nav=True, error={'title': 'Oh jeez...', 'message': u'Something went wrong \xaf\\_(\uFF82)_/\xaf'})
    else:
        user = current_user(session)
        groupledata.start_group_download(gid, user['access_token'])
        return render_template('error.htm', no_nav=True, error={'title': 'I\'m on it!', 'message': downloading_message})
    
@app.route('/<gid>/<name>')
def member(gid, name):
    user = current_user(session)
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
    
if __name__ == '__main__':   
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)#, use_reloader=False)
