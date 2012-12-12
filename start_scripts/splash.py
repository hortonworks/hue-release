import curses
import sh

screen = None
HINT_WIDTH = 3

def make_greet_window():
    H, W = screen.getmaxyx()
    greet_win = screen.subwin(H / 2 - HINT_WIDTH, W, 0, 0)
    greet_win.box()
    greet_win.addstr(1,2,"Hortonworks Data Platform Sandbox")
    greet_win.addstr(2,2,"Version 1.0.4")
    greet_win.addstr(3,2,"http://hortonworks.com")

def make_ip_window():
    H, W = screen.getmaxyx()
    ip_win = screen.subwin(H / 2, W, H / 2 - HINT_WIDTH, 0)
    ip_win.box()
    try:
        ip = sh.head(
                sh.awk(
                    sh.getent("ahosts", sh.hostname().strip()),
                    "{print $1}"),
                n="1").strip()
    except sh.ErrorReturnCode:
        ip_win.addstr(1,2,"===================================")
        ip_win.addstr(2,2,"You have some connectivity issues!")
        ip_win.addstr(3,2,"Check VM setup instructions")
        ip_win.addstr(4,2,"===================================")
    else:
        ip_win.addstr(1,2,"To initiate your Hortonworks Sandbox session,")
        ip_win.addstr(2,2,"please open a browser and enter this address ")
        ip_win.addstr(3,2,"in the browser's address field: ")
        ip_win.addstr(4,2,"http://%s/" % ip)

def make_hint_window():
    H, W = screen.getmaxyx()
    hint_win = screen.subwin(HINT_WIDTH, W, H - HINT_WIDTH, 0)
    hint_win.box()
    hint_win.addstr(1,1,"<Alt+F2> Log in to this virtual machine")

def init_screen():
    curses.noecho()

    make_greet_window()
    make_ip_window()
    make_hint_window()


def main():
    global screen
    screen = curses.initscr()
    init_screen()

    screen.refresh()

    import sys
    if len(sys.argv)>1 and sys.argv[1] == "-s":
        screen.getch()
    else:
        while True:
            try:
                screen.getch()
            except KeyboardInterrupt:
                pass

    curses.endwin()


if __name__ == '__main__':
    main()