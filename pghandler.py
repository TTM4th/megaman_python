import sys
from typing import Callable
import pygame
from pygame import display,Surface,time,event,locals

class PygameHandler:

	def __init__(self,titlebar_caption:str,window_size:tuple[int,int],back_color:tuple[int,int,int]) -> None:
		pygame.init()
		display.set_caption(titlebar_caption)
		self.screen:Surface = display.set_mode(window_size)
		self.backcolor = back_color
		self.clock:time.Clock = time.Clock()

	def run(self,draw_process:Callable[[Surface],None],eventget_process:Callable[[list[event.Event]],None]):
		try:
			while True:
				self.clock.tick(60)
				self.screen.fill(self.backcolor)
				events = event.get()
				if any(_ for _ in events if (_.type == locals.KEYDOWN and _.key == locals.K_ESCAPE) or _.type == locals.QUIT):
					# 「閉じる」ボタンクリックあるいはEscキーが押されたら終了
					self.quit_process()
				else:
					eventget_process(events)
				draw_process(self.screen)
				display.flip()


		except Exception as e:
			print(e)
			print(type(e))
			self.quit_process()
	
	def quit_process(self):
		pygame.quit()
		sys.exit()
