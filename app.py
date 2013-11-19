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

#################
        
@app.template_filter('nicenum')
def nice_num_filter(n):
    return '{:,}'.format(n)

@app.route('/')
def root():
    return render_template('index.htm')
    
@app.route('/channel.html')
def channel():
    return '<script src="//connect.facebook.net/en_US/all.js"></script>'
    
@app.route('/<gid>/')
def grouppage(gid):
    group = groupledata.get_group(gid)
    
    if group == False:
        user = facebook.get_user_from_cookie(request.cookies, GROUPLE_APP_ID, GROUPLE_APP_SECRET)
        return download_group(gid, user)

    stats = {}
    for stat in Group.stats.keys():
        stats[stat] = group.get_stat(stat)
        
    return render_template('group.htm', group=group.get_template_vars(), stats=stats)
    
def download_group(gid, user):
    try:
        feed = groupledata.downloadGroupJSON(gid, user['access_token'])
    except facebook.GraphAPIError as e:
        if e.message == "An unknown error occurred":
            return render_template('error.htm', no_nav=True, error={'title': 'Oh jeez...', 'message': 'That group was too big for this little webapp to handle, try a different group.'})
            
    group = Group(gid, feed['name'])
    groupledata.populate_data(group, feed)
    groupledata.add_group(group)
    return render_template('error.htm', no_nav=True, error={'title': 'Processing...', 'message': 'We\'re crunching the numbers now. Refresh this in a bit to see results.'})
    
@app.route('/<gid>/m/<name>')
def member(gid, name):
    group = groupledata.get_group(gid)
    
    if group == False:
        user = facebook.get_user_from_cookie(request.cookies, GROUPLE_APP_ID, GROUPLE_APP_SECRET)
        return download_group(gid, user)
        
    m = group.get_member(name)
    if m == None:
        return render_template('error.htm', error={'title': 'Member not found', 'message': 'That member doesn\'t exist, dude.'})
        
    stats = {}
    for stat in Member.stats.keys():
        stats[stat] = m.get_stat(stat)
    
    return render_template('member.htm', group=group.get_template_vars(), stats=stats, uid=m.get_uid(), name=m.get_name())
    
if __name__ == '__main__':   
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)#, use_reloader=False)
