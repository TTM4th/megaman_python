from cmath import rect
from enum import Enum
from math import cos, sin,radians
import random
from pygame import Rect,Surface,transform

from image import EnemyImage
from stageobjects import EnemyData
from weapons import BulletObject
IMAGES = EnemyImage()
SIN45=sin(radians(45))
COS45=cos(radians(45))
class EnemyColor(Enum):
    RED=0
    BLUE=1
    ORANGE=2
    GREEN=3
    YELLOW=4

#敵オブジェクトの基底クラス
class Enemy():

    def __init__(self, rect:Rect, images:list[Surface], is_destractable:bool) -> None:
        self._images:list[Surface] = images
        self._image = images[0]
        self._print_rect = rect
        self.vx = 0
        self.vy = 0
        self.isright = False
        self._ismovable = False
        self._is_destractable = is_destractable
        self._hitrect:Rect = self._print_rect
        self._health = 0
        self._attack = 1
        self.live = True
        self.INIT_X = rect.x
        self.INIT_Y = rect.y

    def reset_process(self) -> None:
        pass

    def catch_bullets(self,bullets:list[BulletObject]) -> None:
        if not(self._is_destractable) : return 
        if any(_ for _ in bullets if self._hitrect.colliderect(_.rect)) :
            bullet = next(_ for _ in bullets if self._hitrect.colliderect(_.rect))
            self._live_eval(bullet)
            bullets.remove(bullet)
    
    def catch_player_location(self,p_center_loc:tuple[float,float]):
        pass
    
    def catch_terrain(self,map_obj_rects:list[Rect]):
        pass

    def update(self) -> None:
        if not(self._ismovable):return
        else:
            self._print_rect.x += self.vx
            self._print_rect.y += self.vy
        
    def draw(self, screen_startx: int, screen_starty: int, surface: Surface) -> None:
        surface.blit(self._image, (self._print_rect.x-screen_startx,
                     self._print_rect.y - screen_starty))

    #被弾した弾より受けたダメージから、残体力を計算して生存してるかどうかを評価する
    def _live_eval(self,bullet:BulletObject) -> None:
        self._health -= bullet.power
        #todo:ここに被弾音を入れる
        if self._health <= 0 : self.live = False
        if not(self.live) : self.reset_process()

    #左向きか
    @property
    def isleft(self) -> bool:
        return not(self.isright)

    #接触時に与えるダメージ
    @property
    def attack(self) -> int :
        return self._attack

    #表示用Rect
    @property
    def print_rect(self) -> Rect:
        return self._print_rect

    #判定用Rect
    @property
    def hitrect(self) -> Rect:
        return self._hitrect

#弾を発射する類の敵の基底クラス
class EmittableEnemy(Enemy):
    def __init__(self, rect: Rect, images: list[Surface], is_destractable: bool) -> None:
        super().__init__(rect, images, is_destractable)
        self.isemit = False

    def emit_act(self) -> set[Enemy]:
        return set()

class Mettole(EmittableEnemy):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(Rect(x,y,16,18), [IMAGES.METTOLE_HIDE,IMAGES.METTOLE_APPEAR],True)
        self.color = EnemyColor.YELLOW
        self.CLOSING_COUNT=90
        self.OPENING_COUNT=36
        self.ONELOOPTIME = self.CLOSING_COUNT + self.OPENING_COUNT
        BULLET_V_SCALAR = 3
        self.__BULLET_V_LEFT:set[tuple] = {(-BULLET_V_SCALAR,BULLET_V_SCALAR),(-BULLET_V_SCALAR,0),(-BULLET_V_SCALAR,-BULLET_V_SCALAR)}
        self.__BULLET_V_RIGHT:set[tuple] = {(BULLET_V_SCALAR,BULLET_V_SCALAR),(BULLET_V_SCALAR,0),(BULLET_V_SCALAR,-BULLET_V_SCALAR)}
        self.reset_process()

    def reset_process(self) -> None:
        self.__timer = 0
        self.__isguarding = True
        self._health = 1

    #被弾した弾より受けたダメージから、残体力を計算して生存してるかどうかを評価する（ガード対応）
    def _live_eval(self,bullet:BulletObject) -> None:
        if self.__isguarding:pass#todo:ここでガードした時の音を鳴らす
        else:super()._live_eval(bullet)

    def catch_player_location(self,p_center_loc:tuple[float,float]):
        if self._print_rect.centerx > p_center_loc[0] : self.isright = False
        else : self.isright = True

    def update(self):
        self.__counter()
        self.__get_state()
        #ガード時が０番目、非ガード時が１番目のためint(not(self.__isguarding))で直接参照
        self._image= transform.flip(self._images[int(not(self.__isguarding))], self.isright, False)
        super().update()

    def emit_act(self) -> set[EmittableEnemy]:
        #todo:このタイミングで音を鳴らす
        if self.isleft:
            return {EnemyBullet(self.print_rect.left,self.print_rect.centery,_[0],_[1],self.color) for _ in self.__BULLET_V_LEFT}
        else:
            return {EnemyBullet(self.print_rect.right,self.print_rect.centery,_[0],_[1],self.color) for _ in self.__BULLET_V_RIGHT}


    def draw(self, screen_startx: int, screen_starty: int, surface: Surface) -> None:
        super().draw(screen_startx, screen_starty, surface)

    def __counter(self):
        self.__timer += 1
        if self.__timer > self.ONELOOPTIME : self.__timer = 0

    def __get_state(self) -> None:
        if self.__timer >= self.CLOSING_COUNT:
            self.__isguarding = False
            if self.__timer == self.CLOSING_COUNT + 1 :self.isemit = True
            else : self.isemit = False
        else:
            self.__isguarding = True


class Blaster(EmittableEnemy):

    def __init__(self, x: int, y: int, color:EnemyColor) -> None:
        if color == EnemyColor.RED:
            __images = [IMAGES.BLASTER_RED_CLOSE,IMAGES.BLASTER_RED_OPEN1,IMAGES.BLASTER_RED_OPEN2,IMAGES.BLASTER_RED_OPEN3]
        elif color == EnemyColor.BLUE:
            __images = [IMAGES.BLASTER_BLUE_CLOSE,IMAGES.BLASTER_BLUE_OPEN1,IMAGES.BLASTER_BLUE_OPEN2,IMAGES.BLASTER_BLUE_OPEN3]
        elif color == EnemyColor.ORANGE:
            __images = [IMAGES.BLASTER_ORANGE_CLOSE,IMAGES.BLASTER_ORANGE_OPEN1,IMAGES.BLASTER_ORANGE_OPEN2,IMAGES.BLASTER_ORANGE_OPEN3]
        else:
            raise ValueError("Invalid Color Information by argument value")
        super().__init__(Rect(x, y,17,16), __images, True)
        del __images
        self.color = color
        self.FULLCLOSING_COUNT = 180
        self.OPENING_FRAME = 6
        self.FULLOPEN_COUNT = 100
        self.ONELOOPTIME = self.FULLCLOSING_COUNT + self.FULLOPEN_COUNT + self.OPENING_FRAME * 4
        self.BULLET_V_LEFT = [(-1,-4),(-4,-1),(-4,1),(-1,4)]
        self.BULLET_V_RIGHT = [(1,-4),(4,-1),(4,1),(1,4)]
        self.EMIT_TIMINGS = [13,38,62,87]
        self.reset_process()

    def reset_process(self) -> None:
        self._health = 1
        self.__timer = 0
        self.__isguarding = True
        self.__emit_bullet_counter = 0
        self._hitrect = Rect(self._print_rect.x,self._print_rect.y, 9, self._print_rect.height)
        if self.isleft : self._hitrect.move_ip(self._print_rect.width-self._hitrect.width,0)

    #被弾した弾より受けたダメージから、残体力を計算して生存してるかどうかを評価する（ガード対応）
    def _live_eval(self,bullet:BulletObject) -> None:
        if self.__isguarding:pass#todo:ここでガードした時の音を鳴らす
        else:super()._live_eval(bullet)

    def update(self):
        self.__counter()
        self.__get_state()
        self.__update_image()

    def emit_act(self) -> set[EmittableEnemy]:
        if self.isleft:
            velos = self.BULLET_V_LEFT
            x = self.print_rect.left
        else:
            velos = self.BULLET_V_RIGHT
            x = self.print_rect.right
        v = velos[self.__emit_bullet_counter]
        return {EnemyBullet(x,self.print_rect.centery,v[0],v[1],self.color)}


    def draw(self, screen_startx: int, screen_starty: int, surface: Surface) -> None:
        if self.__isguarding and self.isleft :
            printx = screen_startx + self._hitrect.width - self._print_rect.width
        else :
            printx = screen_startx
        super().draw(printx, screen_starty, surface)
    
    def __counter(self):
        self.__timer += 1
        if self.__timer > self.ONELOOPTIME : self.__timer = 0

    def __get_state(self) -> None:
        if self.__timer - self.FULLCLOSING_COUNT >= self.OPENING_FRAME * 2 and self.__timer - (self.FULLCLOSING_COUNT + self.OPENING_FRAME * 2) <= self.FULLOPEN_COUNT:
            self.__isguarding = False
        else:
            self.__isguarding = True
        if not(self.__isguarding):
            time = self.__timer - (self.FULLCLOSING_COUNT + self.OPENING_FRAME * 2)
            if any(_ for _ in self.EMIT_TIMINGS if time == _) : 
                self.isemit =True
                self.__emit_bullet_counter = self.EMIT_TIMINGS.index(time)
            else : self.isemit =False

    def __update_image(self) -> None:
        if self.__timer < self.FULLCLOSING_COUNT:
            self._image = transform.flip(self._images[0],self.isright,False)
        elif self.__timer < self.FULLCLOSING_COUNT + self.OPENING_FRAME or self.__timer > self.FULLCLOSING_COUNT + self.FULLOPEN_COUNT + self.OPENING_FRAME * 3:
            self._image = transform.flip(self._images[1],self.isright,False)
        elif self.__timer < self.FULLCLOSING_COUNT + self.OPENING_FRAME * 2 or self.__timer > self.FULLCLOSING_COUNT + self.FULLOPEN_COUNT + self.OPENING_FRAME * 2 :
            self._image = transform.flip(self._images[2],self.isright,False)
        else:
            self._image = transform.flip(self._images[3],self.isright,False)

class PickelMan(EmittableEnemy):
    def __init__(self, x: int, y: int) -> None:       
        super().__init__(Rect(x,y,32,24), [IMAGES.PICKELMAN_STAND,IMAGES.PICKELMAN_BEGIN_THROW,IMAGES.PICKELMAN_END_THROW], True)        
        self.BEGINTHROW_FRAME = 6
        self.THROWFINISH_FRAME = self.BEGINTHROW_FRAME * 2
        self.THROW_ONELOOPTIME = self.BEGINTHROW_FRAME + self.THROWFINISH_FRAME #投げた後の姿勢を長めに維持するため
        self.reset_process()

    def reset_process(self) -> None:
        self.__isguarding = True
        self.__isthrowing = False
        self.__waittimer = 0
        self.__throwtimer = 0
        self._health = 10

    #被弾した弾より受けたダメージから、残体力を計算して生存してるかどうかを評価する（ガード対応）
    def _live_eval(self,bullet:BulletObject) -> None:
        if self.__isguarding:pass#todo:ここでガードした時の音を鳴らす
        else:super()._live_eval(bullet)

    def update(self) -> None:
        if self.__isthrowing:
            self.__throw_counter()
        else:
            self.__wait_counter()
        self.__update_image()

    def __throw_counter(self) -> None:
        self.__throwtimer += 1
        if self.__throwtimer > self.THROW_ONELOOPTIME : 
            self.__throwtimer = 0
            self.__isthrowing = False
    
    def __wait_counter(self) -> None:
        self.__waittimer += 1
        if self.__waittimer > 90 : 
            self.__waittimer = 0
            self.__isthrowing = True

    def __get_state(self) -> None:
        pass

    def __update_image(self) -> None:
        if self.__isthrowing:
            if self.__throwtimer < self.BEGINTHROW_FRAME:
                self._image = self._images[1]
            else :
                self._image = self._images[2]
        else :
            self._image = self._images[0]

class ScrewDriver(EmittableEnemy):
    def __init__(self, x: int, y: int, color:EnemyColor) -> None:
        if color == EnemyColor.RED:
            __images = [IMAGES.SCREWDRIVER_RED_OFF,IMAGES.SCREWDRIVER_RED_1,IMAGES.SCREWDRIVER_RED_2,IMAGES.SCREWDRIVER_RED_3]
        elif color == EnemyColor.BLUE:
            __images = [IMAGES.SCREWDRIVER_BLUE_OFF,IMAGES.SCREWDRIVER_BLUE_1,IMAGES.SCREWDRIVER_BLUE_2,IMAGES.SCREWDRIVER_BLUE_3]
        elif color == EnemyColor.ORANGE:
            __images = [IMAGES.SCREWDRIVER_ORANGE_OFF,IMAGES.SCREWDRIVER_ORANGE_1,IMAGES.SCREWDRIVER_ORANGE_2,IMAGES.SCREWDRIVER_ORANGE_3]
        else:
            raise ValueError("Invalid Color Information by argument value")
        super().__init__(Rect((x,y),__images[0].get_size()), __images, True)
        del __images
        self.color = color
        self.SHRINK_Y = self._print_rect.y + 8
        self.GROW_Y = self._print_rect.y
        self.ONEFRAMETIME = 6
        self.ONELOOPTIME = self.ONEFRAMETIME * 4
        self.WAITINGTIME = 60
        self.MAXSHOTCOUNT = 3
        BULLETWIDTH = 6
        BULLET_V_SCALAR = 4
        self.__BULLET_V:set[tuple] = {(self.print_rect.left-BULLETWIDTH,self.print_rect.top,-BULLET_V_SCALAR,0),
                                (self.print_rect.left,self.print_rect.top-BULLETWIDTH,-BULLET_V_SCALAR*COS45,-BULLET_V_SCALAR*SIN45),
                                (self.print_rect.centerx-BULLETWIDTH/2,self.print_rect.top-BULLETWIDTH,0,-BULLET_V_SCALAR),
                                (self.print_rect.right-BULLETWIDTH,self.print_rect.top-BULLETWIDTH,BULLET_V_SCALAR*COS45,-BULLET_V_SCALAR*SIN45),
                                (self.print_rect.right,self.print_rect.top,BULLET_V_SCALAR,0)}
        self.__BULLET_V_U_DOWN:set[tuple] = {(self.print_rect.left-BULLETWIDTH,self.print_rect.bottom,-BULLET_V_SCALAR,0),
                                            (self.print_rect.left,self.print_rect.bottom+BULLETWIDTH,-BULLET_V_SCALAR*COS45,BULLET_V_SCALAR*SIN45),
                                            (self.print_rect.centerx-3,self.print_rect.bottom+BULLETWIDTH,0,BULLET_V_SCALAR),
                                            (self.print_rect.right-BULLETWIDTH,self.print_rect.bottom+BULLETWIDTH,BULLET_V_SCALAR*COS45,BULLET_V_SCALAR*SIN45),
                                            (self.print_rect.right,self.print_rect.bottom,BULLET_V_SCALAR,0)}
        self.upside_down = False
        self.reset_process()

    def reset_process(self) -> None:
        self._health = 3
        self.__isshrinking = True
        self.__timer = 0
        self.__shotcounter = 0
        
    def update(self) -> None:
        self.__get_state()
        self.__update_image()
        self._hitrect = self._print_rect

    #def draw(self, screen_startx: int, screen_starty: int, surface: Surface) -> None:
    #    super().draw(screen_startx, screen_starty, surface)
    
    def emit_act(self) -> set[EmittableEnemy]:
        #todo:このタイミングで音を鳴らす
        if self.upside_down:
            return {EnemyBullet(_[0],_[1],_[2],_[3],self.color) for _ in self.__BULLET_V_U_DOWN}
        else:
            return {EnemyBullet(_[0],_[1],_[2],_[3],self.color) for _ in self.__BULLET_V}

    def __get_state(self) -> None:
        self.__timer += 1
        if self.__timer >= self.WAITINGTIME + self.ONELOOPTIME:
            if self.__shotcounter < self.MAXSHOTCOUNT : 
                self.__shotcounter += 1
                self.__timer -= self.ONELOOPTIME
            else :
                self.__shotcounter = 0
                self.__timer = 0        
        if self.__timer >= self.WAITINGTIME:
            self.__isshrinking = False
            if self.__timer == self.WAITINGTIME + 1:
                self.isemit = True
            else:
                self.isemit = False
        else:
            self.__isshrinking = True            
                

    def __update_image(self) -> None:
        if self.__isshrinking:
            _image = self._images[0]
            if self._print_rect.height !=8 : self._print_rect.inflate_ip(0,-8)
            if not(self.upside_down) :self._print_rect.y = self.SHRINK_Y
            else : self._print_rect.y = self.GROW_Y
        else:
            frame_index = (self.__timer - self.WAITINGTIME) // self.ONEFRAMETIME + 1
            if frame_index > 3 : frame_index = 2
            _image = self._images[frame_index]
            if self._print_rect.height !=16 : self._print_rect.inflate_ip(0,8)
            self._print_rect.y = self.GROW_Y
        self._hitrect = self._print_rect
        self._image = transform.flip(_image,False,self.upside_down)

class BigEYE(Enemy):
    def __init__(self, x: int, y: int, color:EnemyColor) -> None:
        
        if color == EnemyColor.RED:
            __images = [IMAGES.BIGEYE_RED_SHRINK,IMAGES.BIGEYE_RED_GROW]
        elif color == EnemyColor.BLUE:
            __images = [IMAGES.BIGEYE_BLUE_SHRINK,IMAGES.BIGEYE_BLUE_GROW]
        elif color == EnemyColor.ORANGE:
            __images = [IMAGES.BIGEYE_REDORANGE_SHRINK,IMAGES.BIGEYE_REDORANGE_GROW]
        else:
            raise ValueError("Invalid Color Information by argument value")
        super().__init__(Rect((x,y),__images[0].get_size()), __images, True)
        del __images
        self.color = color
        self._ismovable = True
        self._attack = 10
        self.__GROWSIZE = self._images[0].get_size()
        self.__SHRINKSIZE = self._images[1].get_size()
        self.__SHRINK_DIFFERENCE = abs(self._images[0].get_height() - self._images[1].get_height())
        self.reset_process()

    def reset_process(self) -> None:
        self._health = 20
        self.__timer = 0
        self.__island = True

    def catch_player_location(self, p_center_loc: tuple[float, float]):
        if self._print_rect.centerx >= p_center_loc[0] : self.isright = False
        else : self.isright = True

    def update(self) -> None:
        self.__get_state()
        self._hitrect = self._print_rect

    def __get_state(self) -> None:
        self.__timer += 1
        if self.__timer >= 30:
            self.__island = False
        if self.__timer >= 60 : 
            self.__island = True
            self.__timer =0

        if self.__island:
            self._image = self._images[0]
            if abs(self._print_rect.height - self.__SHRINKSIZE) > 0 : self._print_rect.top += self.__SHRINK_DIFFERENCE
            self._print_rect.size = self.__SHRINKSIZE
        else:
            self._image = self._images[1]
            self._print_rect.size = self.__GROWSIZE

    def catch_terrain(self, map_obj_rects: list[Rect]):
        if not(self._ismovable) : return
        eval = lambda pt : [_ for _ in map_obj_rects if _.collidepoint(pt)]
        if any(blk:=eval(self._print_rect.midright)):
            self._print_rect.right = blk[0].left
            self.vx = 0
        elif any(blk:=eval(self._print_rect.midleft)):
            self._print_rect.left = blk[0].right
            self.vx = 0
        if any(blk:=eval(self._print_rect.midtop)) and self.vy < 0: 
            self._print_rect.top = blk[0].bottom
            self.vy = 0
        elif any(blk:=eval(self._print_rect.midbottom)) and self.vy > 0:
            #動作停止時の初期化処理
            self.vy = 0
            self._ismovable = False
            self._print_rect.bottom = blk[0].top
            self.__timer = 0
       
class BumbieHeli(Enemy):
    def __init__(self, x: int, y: int, color:EnemyColor) -> None:
        
        if color == EnemyColor.BLUE:
            __images = [IMAGES.BUMBIE_HELI_B1,IMAGES.BUMBIE_HELI_B2]
        elif color == EnemyColor.GREEN:
            __images = [IMAGES.BUMBIE_HELI_G1,IMAGES.BUMBIE_HELI_G2]
        else:
            raise ValueError("Invalid Color Information by argument value")
        super().__init__(Rect((x,y),__images[0].get_size()), __images, True)
        del __images
        self.color = color
        self._ismovable = True
        self.__ONELOOPFRAME = 12
        self.__ONEPATTERNFRAME = 6
        self.__CHARGE_RANGE = 40
        self.__APPROACHING_FAST_X_SCALAR = 2
        self.__APPROACHING_TIME = self.__CHARGE_RANGE // self.__APPROACHING_FAST_X_SCALAR
        self._attack = 3
        self.reset_process()

    def reset_process(self) -> None:
        if self._print_rect.x != self.INIT_X : self._print_rect.x = self.INIT_X
        if self._print_rect.y != self.INIT_Y : self._print_rect.y = self.INIT_Y
        self.__timer = 0
        self.vx = 0
        self.vy = 0
        self.__approaching = True
        self.p_target_loc : tuple[float,float] = None

    def catch_player_location(self, p_center_loc: tuple[float, float]):
        is_prev_right = self.isright
        if self._print_rect.centerx >= p_center_loc[0] : self.isright = False
        else : self.isright = True

        if self.__approaching : 
            if abs(self._print_rect.centerx - p_center_loc[0]) > self.__CHARGE_RANGE:
                if self.isleft : self.vx = -1
                else : self.vx = 1
            else:
                if self.p_target_loc is None:
                    self.p_target_loc = p_center_loc
                    if self.isleft : self.vx = -self.__APPROACHING_FAST_X_SCALAR
                    else : self.vx = self.__APPROACHING_FAST_X_SCALAR
                    self.vy = (self.p_target_loc[1] - self._print_rect.centery) / self.__APPROACHING_TIME
                elif self._print_rect.collidepoint(self.p_target_loc) or is_prev_right != self.isright:
                    self.vy *= -1
                    self.p_target_loc = None
                    self.__approaching = False
        else:
            #限界点まで上昇した場合、あるいは限界点まで下降した場合はY軸移動をキャンセルする
            eval_y = (self.vy <= 0 and self._print_rect.y <= self.INIT_Y) or (self.vy >=0 and self._print_rect.y >= self.INIT_Y)
            if abs(self._print_rect.centerx - p_center_loc[0]) > self.__CHARGE_RANGE and eval_y : self.__approaching = True
            if eval_y:self.vy = 0

    def update(self) -> None:
        #タイマ更新
        self.__timer += 1
        if self.__timer >= self.__ONELOOPFRAME : self.__timer = 0
        #イメージ
        self._image = transform.flip(self._images[(self.__timer // self.__ONEPATTERNFRAME)],self.isright,False)
        super().update()
        
class Gabyole(Enemy):
    def __init__(self, x: int, y: int, color:EnemyColor) -> None:
        
        if color == EnemyColor.BLUE:
            __images = [IMAGES.GABYOLE_BLUE_1,IMAGES.GABYOLE_BLUE_2]
        elif color == EnemyColor.ORANGE:
            __images = [IMAGES.GABYOLE_ORANGE_1,IMAGES.GABYOLE_ORANGE_2]
        else:
            raise ValueError("Invalid Color Information by argument value")
        super().__init__(Rect((x,y),(__images[0].get_size())), __images, True)
        del __images
        self.color = color
        self._attack = 3
        self.__ONELOOPFRAME = 12
        self.__ONEPATTERNFRAME = 6
        self._MAX_STOP_TIME = 90
        self.__APPROACH_VX = 2.5
        self.__Y_RANGE = 12 
        self.__IDLE_VX = 1
        self.INIT_Y += (16-self.print_rect.height)
        self.reset_process()

    def reset_process(self) -> None:
        self._ismovable = True
        self.__timer = 0
        self.__stop_timer = 0
        if self._print_rect.x != self.INIT_X:self._print_rect.x = self.INIT_X
        if self._print_rect.y != self.INIT_Y:self._print_rect.y = self.INIT_Y

    def catch_bullets(self, bullets: list[BulletObject]) -> None:
        if any(_ for _ in bullets if self._hitrect.colliderect(_.rect)) :
            bullet = next(_ for _ in bullets if self._hitrect.colliderect(_.rect))
            if isinstance(bullet,BulletObject) : #アイススラッシャーのような動きを止める武器の場合もorでここに条件を追加する
                bullets.remove(bullet)
                self._ismovable = False
            else :
                self._live_eval(bullet)

    def catch_player_location(self, p_center_loc: tuple[float, float]):
        #引数をプレイヤーの中心点にしちゃったためだけにこんなになっちゃった、たはは...
        eval_y_value = self._print_rect.bottom
        p_center_y = p_center_loc[1]
        if eval_y_value <= p_center_y + self.__Y_RANGE and eval_y_value > p_center_y - self.__Y_RANGE:
            if self.isleft : self.vx = -self.__APPROACH_VX
            else : self.vx = self.__APPROACH_VX
        else :
            if self.isleft : self.vx = -self.__IDLE_VX
            else : self.vx = self.__IDLE_VX


    def update(self) -> None:
        if self._ismovable:
            self.__timer += 1
            if self.__timer >= self.__ONELOOPFRAME : self.__timer = 0
            image_index = self.__timer // self.__ONEPATTERNFRAME
            self._image = self._images[image_index]
        else :
            self.__stop_timer += 1
            if self.__stop_timer >= self._MAX_STOP_TIME : 
                self.__stop_timer = 0
                self._ismovable = True
        super().update()

    def catch_terrain(self, map_obj_rects: list[Rect]):
        bottom_right = self.print_rect.bottomright
        bottom_left = self.print_rect.bottomleft
        if not(any(_ for _ in map_obj_rects if _.inflate(0,2).collidepoint(bottom_right))):self.isright = False
        elif not(any(_ for _ in map_obj_rects if _.inflate(0,2).collidepoint(bottom_left))):self.isright = True
        

class Pepe(Enemy):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(Rect((x,y),IMAGES.PEPE_1.get_size()), [IMAGES.PEPE_1,IMAGES.PEPE_2],True)
        self._ismovable = True
        self.ONELOOPFRAME = 12
        self.ONEPATTERNFRAME = 6
        self.reset_process()

    def reset_process(self) -> None:
        self.__timer = 0

    def update(self) -> None:
        self.__timer += 1
        if self.__timer >= self.ONELOOPFRAME : self.__timer = 0
        image_index = self.__timer // self.ONEPATTERNFRAME
        self._image = self._images[image_index]

class Mamboo(Enemy):
    def __init__(self, x: int, y: int) -> None:
        
        super().__init__(Rect(x,y,16,16), [IMAGES.MAMBOO_CLOSE,IMAGES.MAMBOO_OPEN],True)
        self.color = EnemyColor.YELLOW
        self._ismovable = True
        self.CLOSING_COUNT=90
        self.OPENING_COUNT=36
        self.ONELOOPTIME = self.CLOSING_COUNT + self.OPENING_COUNT
        self.OPEN_DIFFERENCE = self._images[0].get_height() - self._images[1].get_height()
        self.reset_process()
    
    def reset_process(self) -> None:
        self.__isguarding = True
        self.__timer = 0

    def update(self):
        self.__counter()
        self.__get_state()
        if self.__isguarding:
            self._image=self._images[0]
        else :
            self._image=self._images[1]

    def draw(self, screen_startx: int, screen_starty: int, surface: Surface) -> None:
        if self.__isguarding:
            screen_starty += self.OPEN_DIFFERENCE
        super().draw(screen_startx, screen_starty, surface)

    def __counter(self):
        self.__timer += 1
        if self.__timer > self.ONELOOPTIME : self.__timer = 0

    def __get_state(self) -> None:
        if self.__timer >= self.CLOSING_COUNT:
            self.__isguarding = False
        else:
            self.__isguarding = True

class Camadoomer(Enemy):
    def __init__(self, x: int, y: int, color:EnemyColor) -> None:
        
        if color == EnemyColor.RED:
            __images = [IMAGES.CAMADOOMER_RED_SHRINK,IMAGES.CAMADOOMER_RED_GROW]
        elif color == EnemyColor.BLUE:
            __images = [IMAGES.CAMADOOMER_BLUE_SHRINK,IMAGES.CAMADOOMER_BLUE_GROW]
        else:
            raise ValueError("Invalid Color Information by argument value")
        super().__init__(Rect(x,y,__images[0].get_width(),__images[0].get_height()), __images, True)
        del __images
        self._ismovable = False
        self.__ONEROOPTIME = 60
        self.__ONE_CHAR = 16
        self.__SHRINK_DIFFERENSE = abs(self._images[0].get_height() - self.__ONE_CHAR)
        self.__MAXJUMPHEIGHT = self.__ONE_CHAR * 2
        self.V0MAXTIME = 16
        self.__g = self.__MAXJUMPHEIGHT * 2 * ((self.V0MAXTIME) ** -2)
        self.__v0max = self.V0MAXTIME * self.__g
        self.__long_x = self.__ONE_CHAR * (6 / 2) 
        self.__short_x = self.__ONE_CHAR * (2 / 2)
        self._attack = 2
        self.reset_process()

    def reset_process(self) -> None:    
        if self._print_rect.x != self.INIT_X:self._print_rect.x = self.INIT_X
        if self._print_rect.y != self.INIT_Y + self.__SHRINK_DIFFERENSE : self._print_rect.y = self.INIT_Y + self.__SHRINK_DIFFERENSE
        self._ismovable = False
        self.__timer = 0
        self.vx = 0
        self.vy = 0

    def catch_player_location(self, p_center_loc: tuple[float, float]):
        if self._print_rect.centerx >= p_center_loc[0] : self.isright = False
        else : self.isright = True

    def update(self) -> None:
        self.__timer += 1
        if self.__timer >= self.__ONEROOPTIME : 
            if self.__timer == self.__ONEROOPTIME:
                self._ismovable = True
                if self.isright : self.vx = self.__random_x_velocity()
                else : self.vx = -1 * self.__random_x_velocity()
            self.vy = -self.__v0max + self.__g * (self.__timer - self.__ONEROOPTIME)
        if self._ismovable:
            self._image = self._images[1]
        else:
            self._image = self._images[0]

        super().update()

    def catch_terrain(self, map_obj_rects: list[Rect]):
        if not(self._ismovable) : return
        eval = lambda pt : [_ for _ in map_obj_rects if _.collidepoint(pt)]
        if any(blk:=eval(self._print_rect.midright)):
            self._print_rect.right = blk[0].left
            self.vx = 0
        elif any(blk:=eval(self._print_rect.midleft)):
            self._print_rect.left = blk[0].right
            self.vx = 0
        if any(blk:=eval(self._print_rect.midtop)) and self.vy < 0: 
            self._print_rect.top = blk[0].bottom
            self.vy = 0
        elif any(blk:=eval(self._print_rect.midbottom)) and self.vy > 0:
            #動作停止時の初期化処理
            self.vy = 0
            self._ismovable = False
            self._print_rect.bottom = blk[0].top
            self.__timer = 0

    def __random_x_velocity(self):
        if random.random() < 0.5 : rtn_d = self.__short_x
        else : rtn_d = self.__long_x
        return rtn_d / self.V0MAXTIME

class StickingSusie(Enemy):
    def __init__(self, x: int, y: int, color:EnemyColor) -> None:
        
        if color == EnemyColor.BLUE:
            __images = [IMAGES.SUSIE_BLUE_BLINK,IMAGES.SUSIE_BLUE_SEMIBLINK,IMAGES.SUSIE_BLUE]
        elif color == EnemyColor.ORANGE:
            __images = [IMAGES.SUSIE_ORANGE_BLINK,IMAGES.SUSIE_ORANGE_SEMIBLINK,IMAGES.SUSIE_ORANGE]
        elif color == EnemyColor.RED:
            __images = [IMAGES.SUSIE_RED_BLINK,IMAGES.SUSIE_RED_SEMIBLINK,IMAGES.SUSIE_RED]
        else:
            raise ValueError("Invalid Color Information by argument value")
        super().__init__(Rect(x,y,__images[0].get_width(),__images[0].get_height()), __images, True)
        del __images
        
        self.__ONE_PATTERN_FRAME = 6
        self.__ONE__LOOP_FRAME = self.__ONE_PATTERN_FRAME * len(self._images)
        self.__SUSPEND_FRAME = 180
        self.__WAIT_ANIMATION_FRAME = self.__SUSPEND_FRAME - (self.__ONE__LOOP_FRAME * 2)
        self.__V_SCALAR = 2

        self.is_vertical = False
        self.isdown = False
        self.reset_process()

    def reset_process(self) -> None:
        self._ismovable = False
        self.__suspend_timer = self.__ONE__LOOP_FRAME
        if self._print_rect.x != self.INIT_X : self._print_rect.x = self.INIT_X
        if self._print_rect.y != self.INIT_Y : self._print_rect.y = self.INIT_Y
        self._health = 5
        self._attack = 4

    def update(self) -> None:

        #移動周り処理
        if self._ismovable :
            if self.is_horizonal :
                if self.isleft : self.vx = -self.__V_SCALAR
                else : self.vx = self.__V_SCALAR
            elif self.is_vertical :
                if self.isdown : self.vy = self.__V_SCALAR
                else : self.vy = -self.__V_SCALAR
        else :
            self.vx = 0
            self.vy = 0
            self.__suspend_timer += 1
            if self.__suspend_timer < self.__ONE__LOOP_FRAME:
                self._image = self._images[2 - (self.__suspend_timer // self.__ONE_PATTERN_FRAME)]
            elif (timer:=self.__suspend_timer - (self.__ONE__LOOP_FRAME + self.__WAIT_ANIMATION_FRAME)) >= 0 and self.__suspend_timer < self.__SUSPEND_FRAME:
                self._image = self._images[timer // self.__ONE_PATTERN_FRAME]
            elif self.__suspend_timer >= self.__SUSPEND_FRAME:
                self._ismovable = True
                self.__suspend_timer = 0

        super().update()

    def catch_terrain(self, map_obj_rects: list[Rect]):
        if not(self._ismovable): return
        colided_rects = lambda eval_point : [_ for _ in map_obj_rects if _.collidepoint(eval_point)]
        if self.is_vertical:
            if self.isdown and any(d:=colided_rects(self._print_rect.midbottom)):
                self.isdown = False
                self._ismovable = False
                self._print_rect.bottom = d[0].top
            elif not(self.isdown) and any(d:=colided_rects(self._print_rect.midtop)):
                self.isdown = True
                self._ismovable = False
                self._print_rect.top = d[0].bottom
        elif self.is_horizonal:
            if self.isleft and any(d:=colided_rects(self._print_rect.midleft)):
                self.isright = True
                self._ismovable = False
                self._print_rect.left = d[0].right
            elif self.isright and any(d:=colided_rects(self._print_rect.midright)):
                self.isright = False
                self._ismovable = False
                self._print_rect.right = d[0].left
                
                
    @property
    def is_horizonal(self) -> bool :
        return not(self.is_vertical)

class FootHolder(EmittableEnemy):
    def __init__(self, x: int, y: int, color:EnemyColor) -> None:
        
        if color == EnemyColor.ORANGE:
            images = [IMAGES.FOOTHOLDER_ORANGE_LEFT1,IMAGES.FOOTHOLDER_ORANGE_LEFT2]
        elif color == EnemyColor.GREEN:
            images = [IMAGES.FOOTHOLDER_GREEN_LEFT1,IMAGES.FOOTHOLDER_GREEN_LEFT2]
        else:
            raise ValueError("Invalid Color Information by argument value")
        super().__init__(Rect(x,y,images[0].get_width(),images[0].get_height()), images, True)
        del images
        self.color = color
        self._ismovable = True
        self.ONELOOPFRAME = 12
        self.ONEPATTERNFRAME = 6
        self.reset_process()

    def reset_process(self) -> None:
        self.__timer = 0

    def update(self) -> None:
        self.__timer += 1
        if self.__timer >= self.ONELOOPFRAME : self.__timer = 0
        image_index = (self.__timer // self.ONEPATTERNFRAME)
        self._image=self._images[image_index]
        if self.isright : self._image = transform.flip(self._image,True,False)
        

class KillerBomb(Enemy):

    def __init__(self, x: int, y: int, color:EnemyColor) -> None:
        
        if color == EnemyColor.RED:
            images = [IMAGES.KILLER_RED]
        elif color == EnemyColor.BLUE:
            images = [IMAGES.KILLER_BLUE]
        elif color == EnemyColor.ORANGE:
            images = [IMAGES.KILLER_ORANGE]
        else:
            raise ValueError("Invalid Color Information by argument value")
        super().__init__(Rect((x, y),images[0].get_size()), images, True)
        del images
        self._ismovable = True
        self._image = self._images[0]

    def update(self):
        pass

class Watcher(EmittableEnemy):
    def __init__(self, x: int, y: int) -> None:
        
        super().__init__(Rect((x,y),IMAGES.WATCHER_FULLOPEN.get_size()), [IMAGES.WATCHER_CLOSE,IMAGES.WATCHER_SEMIOPEN,IMAGES.WATCHER_FULLOPEN],True)
        
        self._ismovable = True
        self.ONEPATTERNFRAME = 6
        self.ONELOOPFRAME = len(self._images) * self.ONEPATTERNFRAME
        self.MAX_PATTERN_INDEX = len(self._images) - 1
        self.BEAM_OR_WAIT_TIME = 60
        self.GROW_SEMIOPEN_DIFF = (self._images[1].get_height() - self._images[2].get_height()) // 2
        self.GROW_CLOSED_DIFF = (self._images[0].get_height() - self._images[2].get_height()) // 2
        self.reset_process()

    def reset_process(self) -> None:
        self.__now_image_index = 0
        self.__timer = 0

    def update(self) -> None:
        self.__timer += 1

        if self.__islaunchbeam():
            self.__now_image_index = self.MAX_PATTERN_INDEX
        else:
            if self.__timer < self.ONELOOPFRAME : 
                self.__now_image_index = self.__timer // self.ONEPATTERNFRAME
            elif self.__timer - self.BEAM_OR_WAIT_TIME < self.ONELOOPFRAME:
                self.__now_image_index = self.MAX_PATTERN_INDEX - ((self.__timer - self.BEAM_OR_WAIT_TIME)  // self.ONEPATTERNFRAME)
            else:
                self.__timer = 0

        #print(self.timer,self.now_image_index)
        self._image = self._images[self.__now_image_index]
        
    def draw(self, screen_startx: int, screen_starty: int, surface: Surface) -> None:
        if self.__now_image_index == 0: screen_starty += self.GROW_CLOSED_DIFF
        elif self.__now_image_index == 1: screen_starty += self.GROW_SEMIOPEN_DIFF
        super().draw(screen_startx, screen_starty, surface)

    def __islaunchbeam(self):
        return self.__timer >= self.ONELOOPFRAME and self.__timer < self.ONELOOPFRAME + self.BEAM_OR_WAIT_TIME

class Pickel(Enemy):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(Rect((x,y),IMAGES.PICKEL.get_size()), [IMAGES.PICKEL],False)
        self._ismovable = True
        self.ONEPATTERNFRAME = 4
        self._image = self._images[0]
        self.ONELOOPFRAME = self.ONEPATTERNFRAME * (360 // 90)
        self.reset_process()

    def reset_process(self) -> None:
        self._timer = 0

    def update(self) -> None:
        self._timer +=1
        if self._timer >= self.ONELOOPFRAME: self._timer = 0

        if self._timer < self.ONEPATTERNFRAME:
            self._image = self._images[0]
        elif self._timer < self.ONEPATTERNFRAME * 2:
            self._image = transform.rotate(self._images[0],90)
        elif self._timer < self.ONEPATTERNFRAME * 3:
            self._image = transform.rotate(self._images[0],180)
        else:
            self._image = transform.rotate(self._images[0],-90)


class Chunky(Enemy):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(Rect((x,y),IMAGES.CHUNKY_1.get_size()), [IMAGES.CHUNKY_1,IMAGES.CHUNKY_2],True)
        self._ismovable = True
        self.ONEPATTERNFRAME = 8
        self.ONELOOP_FRAME = self.ONEPATTERNFRAME * 2
        self.reset_process()

    def reset_process(self) -> None:
        self.__timer = 0

    def update(self) -> None:
        self.__timer += 1
        if self.__timer >= self.ONELOOP_FRAME : self.__timer = 0
        self._image = self._images[self.__timer // self.ONEPATTERNFRAME]

class SuperCutter(Enemy):
    def __init__(self, x:int, y:int) -> None:
        super().__init__(Rect((x,y),IMAGES.CUTTER_CLOSE.get_size()), [IMAGES.CUTTER_CLOSE,IMAGES.CUTTER_OPEN], True)
        self._ismovable = True
        self.ONEPATTERNFRAME = 6
        self.ONELOOP_FRAME = self.ONEPATTERNFRAME * 2
        self.PATTERN_HEIGHT_DIFFRENCE = (IMAGES.CUTTER_CLOSE.get_height() - IMAGES.CUTTER_OPEN.get_height()) // 2
        self.reset_process()

    def reset_process(self) -> None:
        self.__timer = 0
        self.__is_opening = False

    def update(self) -> None:
        self.__timer += 1
        if self.__timer >= self.ONELOOP_FRAME:self.__timer = 0

        if self.__timer < self.ONEPATTERNFRAME:
            self.__is_opening = False
        else:
            self.__is_opening = True

        self._image = self._images[int(self.__is_opening)]

    def draw(self, screen_startx: int, screen_starty: int, surface: Surface) -> None:
        if not(self.__is_opening) : screen_starty += self.PATTERN_HEIGHT_DIFFRENCE
        super().draw(screen_startx, screen_starty, surface)


class EnemyBullet(Enemy):
    def __init__(self, x: int, y: int, vx:int, vy:int, color:EnemyColor) -> None:
                
        if color == EnemyColor.RED:
            images = [IMAGES.BULLET_RED]
        elif color == EnemyColor.BLUE:
            images = [IMAGES.BULLET_BLUE]
        elif color == EnemyColor.ORANGE:
            images = [IMAGES.BULLET_ORANGE]
        elif color == EnemyColor.GREEN:
            images = [IMAGES.BULLET_GREEN]
        elif color == EnemyColor.YELLOW:
            images = [IMAGES.BULLET_YELLOW]
        else:
            raise ValueError("Invalid Color Information by argument value")
        super().__init__(Rect(x,y,6,6), images , False)
        self.vx=vx
        self.vy=vy
        self._ismovable = True
        self._attack = 2

class EnemyLibrary:
    ENEMY_DICTIONARY:dict[str,Enemy]={"E00":EnemyBullet,
                                    "E01":Mettole,
                                    "E02":Blaster,
                                    "E03":PickelMan,
                                    "E04":Pickel,
                                    "E05":ScrewDriver,
                                    "E06":BigEYE,
                                    "E09":StickingSusie,
                                    "E10":KillerBomb,
                                    "E11":Watcher,
                                    "E12":BumbieHeli,
                                    "E13":Gabyole,
                                    "E14":Pepe,
                                    "E15":Mamboo,
                                    "E16":Camadoomer,
                                    "E17":FootHolder,
                                    "E18":Chunky,
                                    "E19":SuperCutter
                                    }

    COLOR_DICTIONARY:dict[str,EnemyColor]={"R":EnemyColor.RED,"B":EnemyColor.BLUE,
                                    "Y":EnemyColor.YELLOW,"G":EnemyColor.GREEN,
                                    "O":EnemyColor.ORANGE}
    RIGHT_FLAG:str = 'R'
    DOWN_FLAG:str = 'D'
    UP_FLAG:str = 'U'

    VANISH_ENEMY_TYPE = {EnemyBullet,Pickel}

class EnemyManager:
    def __init__(self,enemies_data:set[EnemyData],screen_width)->None:
        #ステージ上の敵
        self.enemies_data:set[EnemyData] = enemies_data

        self.EXISTWIDTH = screen_width
        self.EXISTHEIGHT_TOP = 0
        self.EXISTHEIGHT_BOTTOM = 0
        #現在表示中Y座標区間に存在する敵
        self.on_range_enemy:set[Enemy] = set()
        #表示範囲内の敵
        self.on_screen_enemy:set[Enemy] = set()

    #EnemyData構造体から敵オブジェクトを生成する
    def __enemy_factory(self,data:EnemyData)->Enemy:
        e_id = data.key[0:3]
        c_id = data.key[3:4]
        if c_id != "N": 
            color = EnemyLibrary.COLOR_DICTIONARY.get(c_id)
            if e_id == "E00":
                obj:Enemy = EnemyLibrary.ENEMY_DICTIONARY.get(e_id)(data.initx,data.inity,0,0,color)
            else :
                obj:Enemy = EnemyLibrary.ENEMY_DICTIONARY.get(e_id)(data.initx,data.inity,color)
        else:
            obj:Enemy = EnemyLibrary.ENEMY_DICTIONARY.get(e_id)(data.initx,data.inity)           
        if isinstance(obj,ScrewDriver) : 
            obj.upside_down = (len(data.key) > 4 and data.key[4:5] == EnemyLibrary.DOWN_FLAG)
        elif isinstance(obj,StickingSusie) :
            if len(data.key) > 4 :
                if data.key[4:5] == EnemyLibrary.DOWN_FLAG:
                    obj.is_vertical = True
                    obj.isdown = True
                elif data.key[4:5] == EnemyLibrary.UP_FLAG:
                    obj.is_vertical = True
                    obj.isdown = False
                elif data.key[4:5] == EnemyLibrary.RIGHT_FLAG:
                    obj.isright = True
        else:
            obj.isright = (len(data.key) > 4 and data.key[4:5] == EnemyLibrary.RIGHT_FLAG)
        return obj

    #表示範囲内の敵を取得　Y軸スクロールに実行すること
    def capture_on_Y(self,now_y_range:Rect):
        self.on_range_enemy.clear()
        self.on_range_enemy = {self.__enemy_factory(_) for _ in self.enemies_data if now_y_range.collidepoint(_.initx,_.inity)}
        self.EXISTHEIGHT_TOP = now_y_range.top
        self.EXISTHEIGHT_BOTTOM = now_y_range.bottom
        self.on_screen_enemy.clear()

    #スクロールアウトかつ死んだ敵を予め復活させる処理
    def reflesh_enemy(self,screen_adjust_x:int) -> None:
        for _ in self.on_range_enemy:
            if not(self.__is_exist_range(_,screen_adjust_x)) and not(self.__is_initloc_in_range(_,screen_adjust_x)) :
                if _.live : _.reset_process() #生きた状態で敵実体および発生場所がスクロールアウトした場合リセット
                else : _.live = True #既に死んでいた場合は再スクロールイン時の復活のため、予めliveフラグにTrueをいれる（死亡判定時に既にリセットをかけてるからリセット不要）

    #表示敵オブジェクトを管理する
    def capture_on_screen(self,screen_adjust_x: int):
        on_range = {_ for _ in self.on_range_enemy if self.__is_exist_range(_, screen_adjust_x) and _.live}
        if not self.on_screen_enemy : 
            #表示敵の集合が空の場合は、取得したスクリーン範囲内の敵を全て入れる
            self.on_screen_enemy = on_range
        else :
            #表示敵の集合が既にある場合はX方向スクロール後に表示する敵だけ追加する
            self.on_screen_enemy |= on_range.symmetric_difference(self.on_screen_enemy)
        del on_range

    #表示範囲内の敵にプレイヤー位置を取得させる
    def catch_player_location(self,p_loc:tuple[int,int]):
        for _ in self.on_screen_enemy:
            _.catch_player_location(p_loc)

    #表示範囲内の敵に表示範囲内のプレイヤーの攻撃に被弾したかチェックさせる
    def catch_bullets(self,bullets:list[BulletObject]):
        for _ in self.on_screen_enemy:
            _.catch_bullets(bullets)

    #表示範囲内の敵を更新させる
    def update(self)->None:
        emit_bullets:set=set()
        for _ in self.on_screen_enemy:
            _.update()
            #弾発射する敵の場合の処理
            if isinstance(_,EmittableEnemy) and _.isemit : emit_bullets |=set(_.emit_act())
        if any(emit_bullets) : self.on_screen_enemy |= emit_bullets

    #表示範囲内の敵に表示範囲内の地形情報を取得させる
    def catch_terrain(self,map_obj_rects)->None:
        for _ in self.on_screen_enemy:
            _.catch_terrain(map_obj_rects)

    #表示範囲内の敵を描画する
    def draw(self, screen_adjust_x: int, screen_adjust_y: int, surface: Surface) -> None:
        self.on_screen_enemy -= {_ for _ in self.on_screen_enemy if not self.__is_exist_range(_,screen_adjust_x) or not _.live}
        for _ in self.on_screen_enemy:
            _.draw(screen_adjust_x, screen_adjust_y, surface)
        #print('objs:{}'.format(len(self.on_screen_enemy)))
    
    #表示範囲内に敵（実体）が存在するか
    def __is_exist_range(self,enemy:Enemy, screen_adjust_x: int) -> bool:
        is_exist_x = enemy.print_rect.left > screen_adjust_x and enemy.print_rect.right < screen_adjust_x + self.EXISTWIDTH + 16
        is_exist_y = enemy.print_rect.top > self.EXISTHEIGHT_TOP and enemy.print_rect.bottom < self.EXISTHEIGHT_BOTTOM
        return is_exist_x and is_exist_y

    #敵発生場所が表示範囲内に存在するか
    def __is_initloc_in_range(self,enemy:Enemy, screen_adjust_x: int) -> bool:
        is_exist_init_x = enemy.INIT_X >  screen_adjust_x and enemy.INIT_X < screen_adjust_x + self.EXISTWIDTH + 16
        is_exist_init_y = enemy.INIT_Y > self.EXISTHEIGHT_TOP and enemy.INIT_Y < self.EXISTHEIGHT_BOTTOM
        return is_exist_init_x and is_exist_init_y
