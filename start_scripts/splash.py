import curses
import sh

screen = curses.initscr()
curses.noecho()

H, W = screen.getmaxyx()

HINT_WIDTH = 3

greet_win = screen.subwin(H / 2 - HINT_WIDTH, W, 0, 0)
greet_win.box()
greet_win.addstr(1,2,"Hortonworks Data Platform Sandbox")
greet_win.addstr(2,2,"Version 1.0.4")
greet_win.addstr(3,2,"http://hortonworks.com")

ip_win = screen.subwin(H / 2, W, H / 2 - HINT_WIDTH, 0)
ip_win.box()
ip = sh.head(
        sh.awk(
            sh.getent("ahosts", sh.hostname().strip()),
            "{print $1}"),
        n="1").strip()

ip_win.addstr(1,2,"Log in to this sandbox by navigating your browser to")
ip_win.addstr(2,2,"http://%s/" % ip)

hint_win = screen.subwin(HINT_WIDTH, W, H - HINT_WIDTH, 0)
hint_win.box()
hint_win.addstr(1,1,"<Alt+F2> Log in to this virtual machine")

screen.refresh()

while True:
    try:
        screen.getch()
    except KeyboardInterrupt:
        pass

curses.endwin()