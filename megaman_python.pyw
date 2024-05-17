#import logging

from pygame import event,Surface
from megaman_python.pghandler import PygameHandler
handler = PygameHandler(3, (0, 0, 0))
from megaman_python.view import PlayingView
playing_view =  PlayingView(handler.screen.get_rect())

def main():
    handler.run(draw_process,eventget_process)
    
def draw_process(screen:Surface) -> None:
    playing_view.draw(screen)
    
def eventget_process(events:list[event.Event]) -> None:
    playing_view.catch_input(events)
    if not(playing_view.is_auto_scrolling()) : playing_view.update_motion()

if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    main()
