
from pygame import Surface , image 

class CharaImageSource:
	def __init__(self):
		self.__STANDSIZE:tuple[int,int] = (21,24)
		self.__RUNSIZE:tuple[int,int] = (24,24)
		self.__FIRESIZE:tuple[int,int] = (32,24)
		self.__RUNFIRESIZE:tuple[int,int] = (32,24)
		self.__JUMPFIRESIZE:tuple[int,int] = (30,30)
		self.__SOURCEIMG:Surface = image.load("picture/m_normal.gif").convert_alpha()
		self.HIT_EFFECT_LARGE:Surface = image.load("picture/hit_effect_large.gif").subsurface(0,0,24,28).convert_alpha()
		self.HIT_EFFECT_SMALL1:Surface = image.load("picture/hit_effect_small1.gif").convert_alpha()
		self.HIT_EFFECT_SMALL2:Surface = image.load("picture/hit_effect_small2.gif").convert_alpha()
		self.HIT_EFFECT_SMALL3:Surface = image.load("picture/hit_effect_small3.gif").convert_alpha()
		self.STAND:Surface = self.__SOURCEIMG.subsurface(0,8,self.__STANDSIZE[0],self.__STANDSIZE[1])
		self.STANDBLINK:Surface = self.__SOURCEIMG.subsurface(24,8,self.__STANDSIZE[0],self.__STANDSIZE[1])
		self.STEPPING:Surface = self.__SOURCEIMG.subsurface(48,8,self.__STANDSIZE[0],self.__STANDSIZE[1])
		self.RUN1:Surface = self.__SOURCEIMG.subsurface(72,8,self.__RUNSIZE[0],self.__RUNSIZE[1])
		self.RUN2:Surface = self.__SOURCEIMG.subsurface(96,8,self.__RUNSIZE[0],self.__RUNSIZE[1])
		self.RUN3:Surface = self.__SOURCEIMG.subsurface(120,8,self.__RUNSIZE[0],self.__RUNSIZE[1])
		self.JUMP:Surface = self.__SOURCEIMG.subsurface(144,2,26,30)
		self.FIRE:Surface = self.__SOURCEIMG.subsurface(176,8,self.__FIRESIZE[0],self.__FIRESIZE[1])
		self.THROW:Surface = self.__SOURCEIMG.subsurface(208,8,self.__FIRESIZE[0],self.__FIRESIZE[1])

		#反転時のズレ調整の共通化のため、ジャンプ中投げorジャンプ中バスターは同サイズでくりぬきした
		self.JUMPFIRE:Surface = self.__SOURCEIMG.subsurface(240,2,self.__JUMPFIRESIZE[0],self.__JUMPFIRESIZE[1])
		self.JUMPTHROW:Surface = self.__SOURCEIMG.subsurface(272,2,self.__JUMPFIRESIZE[0],self.__JUMPFIRESIZE[1])

		self.FIRERUN1:Surface = self.__SOURCEIMG.subsurface(304,8,self.__RUNFIRESIZE[0],self.__RUNFIRESIZE[1])
		self.FIRERUN2:Surface = self.__SOURCEIMG.subsurface(336,8,self.__RUNFIRESIZE[0],self.__RUNFIRESIZE[1])
		self.FIRERUN3:Surface = self.__SOURCEIMG.subsurface(368,8,self.__RUNFIRESIZE[0],self.__RUNFIRESIZE[1])
		self.CRAWLING:Surface = self.__SOURCEIMG.subsurface(400,8,16,24)
		self.CLIMBING:Surface = self.__SOURCEIMG.subsurface(416,3,16,29)
		self.CLIMBINGFIRE:Surface = self.__SOURCEIMG.subsurface(432,3,24,29)
		self.CLIMBINGTHROW:Surface = self.__SOURCEIMG.subsurface(456,3,24,29)
		self.HOLDSTAND:Surface = self.__SOURCEIMG.subsurface(480,8,self.__STANDSIZE[0],self.__STANDSIZE[1])
		self.HOLDSTANDBLINK:Surface = self.__SOURCEIMG.subsurface(504,8,self.__STANDSIZE[0],self.__STANDSIZE[1])
		self.HOLDSTEPPING:Surface = self.__SOURCEIMG.subsurface(528,8,self.__STANDSIZE[0],self.__STANDSIZE[1])
		self.HOLDJUMP:Surface = self.__SOURCEIMG.subsurface(552,2,24,30)
		self.HOLDRUN1:Surface = self.__SOURCEIMG.subsurface(576,8,self.__RUNSIZE[0],self.__RUNSIZE[1])
		self.HOLDRUN2:Surface = self.__SOURCEIMG.subsurface(600,8,self.__RUNSIZE[0],self.__RUNSIZE[1])
		self.HOLDRUN3:Surface = self.__SOURCEIMG.subsurface(624,8,self.__RUNSIZE[0],self.__RUNSIZE[1])
		self.DAMAGED:Surface = self.__SOURCEIMG.subsurface(648,4,26,28)
		self.FALLEN:Surface = self.__SOURCEIMG.subsurface(680,8,28,24)
		self.WARP:Surface = self.__SOURCEIMG.subsurface(712,0,8,32)
		self.WARPLAND1:Surface = self.__SOURCEIMG.subsurface(720,0,24,32)
		self.WARPLAND2:Surface = self.__SOURCEIMG.subsurface(744,0,24,32)
		del self.__STANDSIZE
		del self.__RUNSIZE
		del self.__FIRESIZE
		del self.__RUNFIRESIZE
		del self.__JUMPFIRESIZE
		del self.__SOURCEIMG

class EnemyImage():
	
	def __init__(self) -> None:
		self.__SOURCEIMG:Surface = image.load("picture/enemies.gif").convert_alpha()
		self.METTOLE_HIDE:Surface = self.__SOURCEIMG.subsurface(0,0,18,16)
		self.METTOLE_APPEAR:Surface = self.__SOURCEIMG.subsurface(24,0,18,16)
		self.BUMBIE_HELI_G1:Surface = self.__SOURCEIMG.subsurface(64,0,16,20)
		self.BUMBIE_HELI_G2:Surface = self.__SOURCEIMG.subsurface(80,0,16,20)
		self.BUMBIE_HELI_B1:Surface = self.__SOURCEIMG.subsurface(96,0,16,20)
		self.BUMBIE_HELI_B2:Surface = self.__SOURCEIMG.subsurface(112,0,16,20)
		self.PICKELMAN_STAND:Surface = self.__SOURCEIMG.subsurface(136,0,32,24)
		self.PICKELMAN_BEGIN_THROW:Surface = self.__SOURCEIMG.subsurface(168,0,32,24)
		self.PICKELMAN_END_THROW:Surface = self.__SOURCEIMG.subsurface(200,0,24,24)
		self.PICKEL:Surface = self.__SOURCEIMG.subsurface(230,5,11,12)
		self.BIGEYE_BLUE_SHRINK:Surface = self.__SOURCEIMG.subsurface(304,8,32,40)
		self.BIGEYE_BLUE_GROW:Surface = self.__SOURCEIMG.subsurface(336,0,32,48)
		self.BIGEYE_RED_SHRINK:Surface = self.__SOURCEIMG.subsurface(368,8,32,40)
		self.BIGEYE_RED_GROW:Surface = self.__SOURCEIMG.subsurface(400,0,32,48)
		self.BIGEYE_REDORANGE_SHRINK:Surface = self.__SOURCEIMG.subsurface(432,8,32,40)
		self.BIGEYE_REDORANGE_GROW:Surface = self.__SOURCEIMG.subsurface(464,0,32,48)
		self.SUSIE_RED_BLINK:Surface = self.__SOURCEIMG.subsurface(0,24,16,16)
		self.SUSIE_RED_SEMIBLINK:Surface = self.__SOURCEIMG.subsurface(16,24,16,16)
		self.SUSIE_RED:Surface = self.__SOURCEIMG.subsurface(32,24,16,16)
		self.SUSIE_ORANGE_BLINK:Surface = self.__SOURCEIMG.subsurface(48,24,16,16)
		self.SUSIE_ORANGE_SEMIBLINK:Surface = self.__SOURCEIMG.subsurface(64,24,16,16)
		self.SUSIE_ORANGE:Surface = self.__SOURCEIMG.subsurface(80,24,16,16)
		self.SUSIE_BLUE_BLINK:Surface = self.__SOURCEIMG.subsurface(96,24,16,16)
		self.SUSIE_BLUE_SEMIBLINK:Surface = self.__SOURCEIMG.subsurface(112,24,16,16)
		self.SUSIE_BLUE:Surface = self.__SOURCEIMG.subsurface(128,24,16,16)
		self.GABYOLE_BLUE_1:Surface = self.__SOURCEIMG.subsurface(152,32,16,8)
		self.GABYOLE_BLUE_2:Surface = self.__SOURCEIMG.subsurface(168,32,16,8)
		self.GABYOLE_ORANGE_1:Surface = self.__SOURCEIMG.subsurface(184,32,16,8)
		self.GABYOLE_ORANGE_2:Surface = self.__SOURCEIMG.subsurface(200,32,16,8)
		self.PEPE_1:Surface = self.__SOURCEIMG.subsurface(224,24,24,16)
		self.PEPE_2:Surface = self.__SOURCEIMG.subsurface(248,24,24,16)
		self.CUTTER_CLOSE:Surface = self.__SOURCEIMG.subsurface(0,46,16,13)
		self.CUTTER_OPEN:Surface = self.__SOURCEIMG.subsurface(16,43,16,20)
		self.BLASTER_RED_CLOSE:Surface = self.__SOURCEIMG.subsurface(40,48,9,16)
		self.BLASTER_RED_OPEN1:Surface = self.__SOURCEIMG.subsurface(56,48,9,16)
		self.BLASTER_RED_OPEN2:Surface = self.__SOURCEIMG.subsurface(72,48,9,16)
		self.BLASTER_RED_OPEN3:Surface = self.__SOURCEIMG.subsurface(88,48,17,16)
		self.BLASTER_ORANGE_CLOSE:Surface = self.__SOURCEIMG.subsurface(40+88,48,9,16)
		self.BLASTER_ORANGE_OPEN1:Surface = self.__SOURCEIMG.subsurface(56+88,48,9,16)
		self.BLASTER_ORANGE_OPEN2:Surface = self.__SOURCEIMG.subsurface(72+88,48,9,16)
		self.BLASTER_ORANGE_OPEN3:Surface = self.__SOURCEIMG.subsurface(88+88,48,17,16)
		self.BLASTER_BLUE_CLOSE:Surface = self.__SOURCEIMG.subsurface(40+88+88,48,9,16)
		self.BLASTER_BLUE_OPEN1:Surface = self.__SOURCEIMG.subsurface(56+88+88,48,9,16)
		self.BLASTER_BLUE_OPEN2:Surface = self.__SOURCEIMG.subsurface(72+88+88,48,9,16)
		self.BLASTER_BLUE_OPEN3:Surface = self.__SOURCEIMG.subsurface(88+88+88,48,17,16)
		self.MAMBOO_CLOSE:Surface = self.__SOURCEIMG.subsurface(8,72,16,16)
		self.MAMBOO_OPEN:Surface = self.__SOURCEIMG.subsurface(24,67,17,21)
		self.CAMADOOMER_BLUE_SHRINK:Surface = self.__SOURCEIMG.subsurface(48,79,14,10)
		self.CAMADOOMER_BLUE_GROW:Surface = self.__SOURCEIMG.subsurface(64,70,14,19)
		self.CAMADOOMER_RED_SHRINK:Surface = self.__SOURCEIMG.subsurface(48+32,79,14,10)
		self.CAMADOOMER_RED_GROW:Surface = self.__SOURCEIMG.subsurface(64+32,70,14,19)
		self.SCREWDRIVER_ORANGE_OFF:Surface = self.__SOURCEIMG.subsurface(120,81,16,8)
		self.SCREWDRIVER_ORANGE_1:Surface = self.__SOURCEIMG.subsurface(136,73,16,16)
		self.SCREWDRIVER_ORANGE_2:Surface = self.__SOURCEIMG.subsurface(160,73,16,16)
		self.SCREWDRIVER_ORANGE_3:Surface = self.__SOURCEIMG.subsurface(184,73,16,16)
		self.SCREWDRIVER_BLUE_OFF:Surface = self.__SOURCEIMG.subsurface(120+88,81,16,8)
		self.SCREWDRIVER_BLUE_1:Surface = self.__SOURCEIMG.subsurface(136+88,73,16,16)
		self.SCREWDRIVER_BLUE_2:Surface = self.__SOURCEIMG.subsurface(160+88,73,16,16)
		self.SCREWDRIVER_BLUE_3:Surface = self.__SOURCEIMG.subsurface(184+88,73,16,16)
		self.SCREWDRIVER_RED_OFF:Surface = self.__SOURCEIMG.subsurface(120+88+88,81,16,8)
		self.SCREWDRIVER_RED_1:Surface = self.__SOURCEIMG.subsurface(136+88+88,73,16,16)
		self.SCREWDRIVER_RED_2:Surface = self.__SOURCEIMG.subsurface(160+88+88,73,16,16)
		self.SCREWDRIVER_RED_3:Surface = self.__SOURCEIMG.subsurface(184+88+88,73,16,16)
		self.WATCHER_CLOSE:Surface = self.__SOURCEIMG.subsurface(0,109,16,19)
		self.WATCHER_SEMIOPEN:Surface = self.__SOURCEIMG.subsurface(16,106,16,24)
		self.WATCHER_FULLOPEN:Surface = self.__SOURCEIMG.subsurface(32,97,16,42)
		self.CRAZYRAZY_1:Surface = self.__SOURCEIMG.subsurface(144,96,32,31)
		self.CRAZYRAZY_2:Surface = self.__SOURCEIMG.subsurface(176,96,32,31)
		self.CRAZYRAZY_3:Surface = self.__SOURCEIMG.subsurface(208,96,32,31)
		self.CRAZYRAZY_UP1:Surface = self.__SOURCEIMG.subsurface(240,96,32,24)
		self.CRAZYRAZY_UP2:Surface = self.__SOURCEIMG.subsurface(272,96,32,24)
		self.CRAZYRAZY_UP3:Surface = self.__SOURCEIMG.subsurface(304,96,32,27)
		self.FOOTHOLDER_ORANGE_LEFT1:Surface = self.__SOURCEIMG.subsurface(0,144,24,32)
		self.FOOTHOLDER_ORANGE_LEFT2:Surface = self.__SOURCEIMG.subsurface(24,144,24,32)
		self.FOOTHOLDER_ORANGE_RIGHT1:Surface = self.__SOURCEIMG.subsurface(48,144,24,32)
		self.FOOTHOLDER_ORANGE_RIGHT2:Surface = self.__SOURCEIMG.subsurface(72,144,24,32)
		self.FOOTHOLDER_GREEN_LEFT1:Surface = self.__SOURCEIMG.subsurface(112,144,24,32)
		self.FOOTHOLDER_GREEN_LEFT2:Surface = self.__SOURCEIMG.subsurface(136,144,24,32)
		self.FOOTHOLDER_GREEN_RIGHT1:Surface = self.__SOURCEIMG.subsurface(160,144,24,32)
		self.FOOTHOLDER_GREEN_RIGHT2:Surface = self.__SOURCEIMG.subsurface(184,144,24,32)
		self.CHUNKY_1:Surface = self.__SOURCEIMG.subsurface(224,144,16,16)
		self.CHUNKY_2:Surface = self.__SOURCEIMG.subsurface(224,168,16,16)
		self.WALLFIRE_SHRINK1:Surface = self.__SOURCEIMG.subsurface(256,144,8,16)
		self.WALLFIRE_SHRINK2:Surface = self.__SOURCEIMG.subsurface(256,168,8,16)
		self.WALLFIRE_GROW1:Surface = self.__SOURCEIMG.subsurface(280,144,64,16)
		self.WALLFIRE_GROW2:Surface = self.__SOURCEIMG.subsurface(280,168,64,16)
		self.JOE_STAND:Surface = self.__SOURCEIMG.subsurface(8,184,26,24)
		self.JOE_FIRE1:Surface = self.__SOURCEIMG.subsurface(40,184,24,24)
		self.JOE_FIRE2:Surface = self.__SOURCEIMG.subsurface(64,184,24,24)
		self.JOE_JUMP:Surface = self.__SOURCEIMG.subsurface(88,176,28,32)
		self.KILLER_BLUE:Surface = self.__SOURCEIMG.subsurface(137,193,16,16)
		self.KILLER_ORANGE:Surface = self.__SOURCEIMG.subsurface(160,193,16,16)
		self.KILLER_RED:Surface = self.__SOURCEIMG.subsurface(184,193,16,16)
		self.BBBOMB_MOTHER_BLUE:Surface = self.__SOURCEIMG.subsurface(208,197,16,12)
		self.BBBOMB_CHILD_BLUE:Surface = self.__SOURCEIMG.subsurface(224,203,8,6)
		self.BBBOMB_MOTHER_RED:Surface = self.__SOURCEIMG.subsurface(208+24,197,16,12)
		self.BBBOMB_CHILD_RED:Surface = self.__SOURCEIMG.subsurface(224+24,203,8,6)
		self.LIFT_GREEN:Surface = self.__SOURCEIMG.subsurface(0,224,32,16)
		self.LIFT_GREEN_FOLD_MIDDLE:Surface = self.__SOURCEIMG.subsurface(40,224,24,22)
		self.LIFT_GREEN_FOLD:Surface = self.__SOURCEIMG.subsurface(72,224,12,28)
		self.LIFT_RED:Surface = self.__SOURCEIMG.subsurface(0+96,224,32,16)
		self.LIFT_RED_FOLD_MIDDLE:Surface = self.__SOURCEIMG.subsurface(40+96,224,24,22)
		self.LIFT_RED_FOLD:Surface = self.__SOURCEIMG.subsurface(72+96,224,12,28)
		self.WALLTHUNDER_1:Surface = self.__SOURCEIMG.subsurface(360,112,64,16)
		self.WALLTHUNDER_2:Surface = self.__SOURCEIMG.subsurface(360,128,64,16)
		self.BULLET_YELLOW:Surface = self.__SOURCEIMG.subsurface(48,5,6,6)
		self.BULLET_RED:Surface = self.__SOURCEIMG.subsurface(112,53,6,6)
		self.BULLET_ORANGE:Surface = self.__SOURCEIMG.subsurface(200,53,6,6)
		self.BULLET_BLUE:Surface = self.__SOURCEIMG.subsurface(288,53,6,6)
		self.BULLET_GREEN:Surface = self.__SOURCEIMG.subsurface(336,109,6,6)
		self.WATCHER_BEAM1:Surface = self.__SOURCEIMG.subsurface(48,108,24,6)
		self.WATCHER_BEAM2:Surface = self.__SOURCEIMG.subsurface(48,122,24,6)
		del self.__SOURCEIMG
		
class BusterBulletImage():

	def __init__(self):
		self.BUSTERBULLET = image.load("picture/mm1weaponsheet.gif").convert_alpha().subsurface(64,9,8,6)


class Meter():

	def __init__(self):
		self._METERIMG:Surface  = image.load("picture/meter.gif").convert_alpha()
		self.METER_BG:Surface  = self._METERIMG.subsurface(0,0,8,56)
		self.HEALTH_MEM:Surface  = self._METERIMG.subsurface(10,54,6,1)
		self.ELEC_MEM:Surface  = self._METERIMG.subsurface(19,54,6,1)
		self.ICE_MEM:Surface  = self._METERIMG.subsurface(28,54,6,1)
		self.FIRE_MEM:Surface  = self._METERIMG.subsurface(37,54,6,1)
		self.BOMB_MEM:Surface  = self._METERIMG.subsurface(46,54,6,1)
		self.GUTS_MEM:Surface  = self._METERIMG.subsurface(55,54,6,1)
		self.CUT_MEM:Surface  = self._METERIMG.subsurface(64,54,6,1)
		self.HEALTH_DRAWPOS:tuple[int,int] = (24,17)
		self.WEAPON_DRAWPOS:tuple[int,int] = (self.HEALTH_DRAWPOS[0]-self.METER_BG.get_rect().width,17)
		self.MEMMARGIN:int = 1
		self.__health:int = 0
		self.HEALTH_MEMORY_X:int = self.HEALTH_DRAWPOS[0] + self.MEMMARGIN
		self.LOWESTMEMORY_Y:int = self.HEALTH_DRAWPOS[1] + self.METER_BG.get_rect().height - 2
		self.WEAPON_MEMORY_X:int = self.WEAPON_DRAWPOS[0] + self.MEMMARGIN
		del self._METERIMG

	def get_health(self,health:int):
		self.__health = health

	def draw(self,surface:Surface):
		surface.blit(self.METER_BG,self.HEALTH_DRAWPOS)
		for i in range(self.__health):
			surface.blit(self.HEALTH_MEM,(self.HEALTH_MEMORY_X,self.LOWESTMEMORY_Y - (i + i) )) #iにiを足しているのはメモリ間1ピクセルのマージンのため
		#ここから先武器エネルギー
		#surface.blit(self.meter_bg,self.WEAPON_DRAWPOS)
		#[surface.blit(self.cutmem,(self.weapon_memoryX,self.lowestmemoryY - (i + i) )) for i in range(28)]

class Tile():

	def __init__(self,path:str,tilerow_counts:int,tilecolumn_counts:int) -> None:
		self.ONESIDE:int = 16
		self.__source:Surface = image.load(path).convert_alpha()
		self.TILELIST:list[Surface]=[]
		for y in range(tilerow_counts):
			for x in range(tilecolumn_counts):
				self.TILELIST.append(self.__source.subsurface(x+1+self.ONESIDE*x,y+1+self.ONESIDE*y,self.ONESIDE,self.ONESIDE))
		del self.__source
	
class CutManTile(Tile):
	
	def __init__(self) -> None:
		super().__init__("picture/mm1cuttiles.gif",4,9)
		self.AILAS = {"start_pipe":0,
					"middle_pipe":1,
					"end_pipe":2,
					"block1":3,
					"block2":4,
					"shutter":5,
					"shadowTile":6,
					"Tile":7,
					"blank":8,
					"sky":9,
					"laddar":10,
					"needle":11,
					"shadow_wall":12,
					"wall":13,
					"floor":14,
					"window1":15,
					"window2":16,
					"vertical_pipe":17,
					"shutter_pipe1":18,
					"shutter_pipe2":19,
					"cutter_nob":20,
					"cutter_left":21,
					"cutter_lefthatch_down":22,
					"cutter_righthatch_down":23,
					"cutter_right":24,
					"rock_upleft":25,
					"rock_upright":26,
					"cutter_lefthatch":27,
					"cutter_righthatch":28,
					"cutter_leftpipe":29,
					"cutter_rightpipe":30,
					"cutter_roofleft":31,
					"cutter_roofmiddle":32,
					"cutter_roofright":33,
					"rock_downleft":34,
					"rock_downright":35}
		self.TILES:dict = {alias:self.TILELIST[index] for alias,index in self.AILAS.items()}
