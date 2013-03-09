from fabric.api import run, put
from fabric.api import env
from fabric.utils import abort
import os

# The default host on which to deploy, etc
env.hosts = ['192.168.4.77']
env.collect_cmd = '/home/dgolliher/photo-frame-project/bin/python /home/dgolliher/photo-frame-project/webremote/manage.py collectstatic --noinput'

def home2():
    env.user = 'pi'
    env.hosts = ['192.168.4.76']
    env.collect_cmd = '/home/pi/photo-frame-project/bin/python /home/pi/photo-frame-project/webremote/manage.py collectstatic --noinput'

def officetv():
    env.user = 'pi'
    env.hosts = ['192.168.4.17']
    env.collect_cmd = '/home/pi/photo-frame-project/bin/python /home/pi/photo-frame-project/webremote/manage.py collectstatic --noinput'
    
def test():
    env.hosts = ['192.168.4.77']
    collect_cmd = '/home/dgolliher/photo-frame-project/bin/python /home/dgolliher/photo-frame-project/webremote/manage.py collectstatic --noinput'

def deploy():
    if not os.path.exists('webremote'):
        abort("I can't file webremote.   Are you in the right directory?")

    print "Copying .py files over"
    put('*.py','photo-frame-project', mode=0755)
    put('*.sh','photo-frame-project', mode=0755)
    put('webremote.html','photo-frame-project/webroot', mode=0644)
    print "Copying Django project over"
    put('webremote','photo-frame-project')
    print "Collecting static files"
    run(env.collect_cmd)
    
def kill():
    run('pkill -f "python ./photoframe.py"')
    
def restart():
    # Relies on watchmedo monitoring photoframe.py
    run('touch photo-frame-project/photoframe.py')

def project_name():
	print "Hackers Photo Frame by Darrell Golliher"
	print "A hobby project from early 2013."
