from fabric.api import run, put
from fabric.api import env

# The default host on which to deploy, etc
env.hosts = ['192.168.4.77']
collect_cmd = '/home/dgolliher/photo-frame-project/bin/python /home/dgolliher/photo-frame-project/webremote/manage.py collectstatic --noinput'

def officetv():
    env.user = 'pi'
    env.hosts = ['192.168.4.75']
    collect_cmd = '/home/pi/photo-frame-project/bin/python /home/dgolliher/photo-frame-project/webremote/manage.py collectstatic --noinput'
    
def test():
    env.hosts = ['192.168.4.77']
    collect_cmd = '/home/dgolliher/photo-frame-project/bin/python /home/dgolliher/photo-frame-project/webremote/manage.py collectstatic --noinput'

def deploy():
    print "Copying .py files over"
    put('photoframe-src/*.py','photo-frame-project', mode=0755)
    put('photoframe-src/*.sh','photo-frame-project', mode=0755)
    put('photoframe-src/webremote.html','photo-frame-project/webroot', mode=0644)
    print "Copying Django project over"
    put('photoframe-src/webremote','photo-frame-project')
    print "Collecting static files"
    run(collect_cmd)

    
def kill():
    run('pkill -f "python ./photoframe.py"')
    
def restart():
    # Relies on watchmedo monitoring photoframe.py
    run('touch photo-frame-project/photoframe.py')

def project_name():
	print "Hackers Photo Frame by Darrell Golliher"
	print "A hobby project from early 2013."
