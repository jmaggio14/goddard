import Tkinter as tk
import os

from mainapp import MainApplication
from TopMenu import TopMenu

def start(client_queue_cmd, client_queue_log, client_queue_telem, server_ip):
    """
    Start graphical interface for client.

    Args:
        client_queue_in: queue to get telemetry and logging info
        client_queue_out: queue to communicate commands
        server_ip: server IP address for rtsp stream access
    """
    root = tk.Tk()   # get root window

    # define mainapp instance
    m = MainApplication(root, client_queue_cmd, client_queue_log, client_queue_telem, server_ip)
    root.protocol("WM_DELETE_WINDOW", m.close_)

    # menu
    menu_ = TopMenu(root, 'config.json', client_queue_cmd)
    root.config(menu=menu_)

    # title and icon
    root.wm_title('Hyperloop Imaging Team')
    img = tk.PhotoImage(os.path.join(os.getcwd(), 'assets/rit_imaging_team.png'))
    root.tk.call('wm', 'iconphoto', root._w, img)

    # run forever
    root.mainloop()

if __name__=='__main__':
    from Queue import Queue

    in_queue = Queue()
    out_queue = Queue()
    server_ip = 'hyperlooptk1.student.rit.edu'

    start(in_queue, out_queue, server_ip)

    