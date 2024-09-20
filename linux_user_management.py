import subprocess
import pwd

def get_users():
    users = []
    for user in pwd.getpwall():
        if user.pw_uid >= 1000 and user.pw_uid < 65534: # to not display weird users
            users.append({
                'username': user.pw_name,
                'fullname': user.pw_gecos.split(',')[0],
                'locked': is_user_locked(user.pw_name)
            })
    return users

def is_user_locked(username):
    try:
        output = subprocess.check_output(['sudo', 'passwd', '-S', username], stderr=subprocess.DEVNULL).decode()
        return 'L' in output.split()[1]
    except subprocess.CalledProcessError:
        return False

def create_user(username, fullname, password):
    try:
        subprocess.run(['sudo', 'useradd', '-m', '-c', fullname, username], check=True)
        subprocess.run(['sudo', 'chpasswd'], input=f"{username}:{password}"
                       , universal_newlines=True, check=True) # crashes without universal_newlines=True
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating user: {e}")
        return False

def delete_user(username):
    try:
        subprocess.run(['sudo', 'userdel', '-r', username], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error deleting user: {e}")
        return False

def lock_user(username):
    try:
        subprocess.run(['sudo', 'usermod', '-L', username], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error locking user: {e}")
        return False

def unlock_user(username):
    try:
        subprocess.run(['sudo', 'usermod', '-U', username], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error unlocking user: {e}")
        return False
