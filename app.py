import os
from flask import Flask
from apscheduler.scheduler import Scheduler

# Start the scheduler
sched = Scheduler()
sched.start()

app = Flask(__name__)

@app.route('/')
def root():
    return 'Hello World!'

if __name__ == '__main__':
    #sched.add_interval_job(poo, seconds=1)
    
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)#, use_reloader=False)
