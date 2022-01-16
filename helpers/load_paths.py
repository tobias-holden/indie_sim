import os


def load_box_paths(user_path=None, parser_default='HPC'):

    if not user_path :
        user_path = os.path.expanduser('~')
        if 'jlg1657' in user_path :
            user_path = 'E:/'
        if 'cygwin' in user_path :
            netid = os.path.split(user_path)[1]
            user_path = os.path.join('C:/Users/', netid)
        if 'mrung' in user_path :
            user_path = 'C:/Users/mrung'
        if 'tmh6260' in user_path : 
            user_path = 'C:/Users/tmh6260'
    home_path = os.path.join(user_path, 'Box', 'NU-malaria-team')
    data_path = os.path.join(home_path, 'data', 'nxtek')
    project_path = os.path.join(home_path, 'projects', 'ghana_nxtek')

    return data_path, project_path
