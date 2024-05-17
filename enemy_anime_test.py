
from pygame import Surface,event
from megaman_python.pghandler import PygameHandler
runObj = PygameHandler("test_view",(640,128),(128,255,128))
from megaman_python.player import BulletObject
from megaman_python.enemy import EnemyData,EnemyManager

ONE_LINE_Y = 0
ONE_SCREEN_START = 0
TWO_LINE_Y = ONE_LINE_Y + 32
WIDTH = runObj.screen.get_width()

enemy_list = {EnemyData("E01N",8,ONE_LINE_Y),
				EnemyData("E02R",32,ONE_LINE_Y),
				EnemyData("E02B",50,ONE_LINE_Y),
				EnemyData("E02OR",68,ONE_LINE_Y),
				EnemyData("E03N",93,ONE_LINE_Y),
				EnemyData("E05R",128,ONE_LINE_Y),
				EnemyData("E05O",144,ONE_LINE_Y),
				EnemyData("E05B",160,ONE_LINE_Y),
				EnemyData("E06R",178,ONE_LINE_Y),
				EnemyData("E06B",210,ONE_LINE_Y),
				EnemyData("E06O",242,ONE_LINE_Y),
				EnemyData("E12B",0+8,TWO_LINE_Y),
				EnemyData("E12G",16+8+2,TWO_LINE_Y),
				EnemyData("E13B",36+8,TWO_LINE_Y+8),
				EnemyData("E13O",52+8+2,TWO_LINE_Y+8),
				EnemyData("E14N",70+8+2,TWO_LINE_Y),
				EnemyData("E15N",100+8,TWO_LINE_Y),
				EnemyData("E16B",120+8,TWO_LINE_Y),
				EnemyData("E16R",136+8,TWO_LINE_Y),
				EnemyData("E09R",274+4,ONE_LINE_Y),
				EnemyData("E09B",290+4,ONE_LINE_Y),
				EnemyData("E09O",306+4,ONE_LINE_Y),
				EnemyData("E17O",274,TWO_LINE_Y),
				EnemyData("E17G",306,TWO_LINE_Y),
				EnemyData("E10B",324+4,ONE_LINE_Y),
				EnemyData("E10R",340+4+2,ONE_LINE_Y),
				EnemyData("E10O",356+4+6,ONE_LINE_Y),
				EnemyData("E11N",390,ONE_LINE_Y),
				EnemyData("E04N",408,ONE_LINE_Y),
				EnemyData("E18N",340,TWO_LINE_Y),
				EnemyData("E19N",360,TWO_LINE_Y),
				EnemyData("E00R",376,TWO_LINE_Y+16),
				EnemyData("E00B",384,TWO_LINE_Y+16),
				EnemyData("E00O",392,TWO_LINE_Y+16),
				EnemyData("E00G",400,TWO_LINE_Y+16),
				EnemyData("E00Y",408,TWO_LINE_Y+16),
				EnemyData("E00G",400,TWO_LINE_Y+16)} #同じ位置に同じキャラクタを置いた重複キャラも読み出し可能になる。

manager = EnemyManager(enemy_list,runObj.screen.get_width())
manager.capture_on_Y(runObj.screen.get_rect())
bullets:list[BulletObject]=[]

def main():
	runObj.run(testing_process,event_capture)
		
def testing_process(screen:Surface):
	manager.catch_bullets(bullets)
	manager.capture_on_screen(0)
	manager.update()
	manager.draw(ONE_SCREEN_START,ONE_LINE_Y,screen)
		

def event_capture(events:list[event.Event]) -> None:
	pass

if __name__ =="__main__":
	main()
