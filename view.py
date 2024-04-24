from enum import IntEnum
from typing import Callable
from pygame import Rect,event
from stageobjects import ObjManager,StageEnum
from player import PlayerHandler
from enemy import EnemyManager

class ScrollYFlag(IntEnum):
    UP = -1
    DOWN = 1
    STAY = 0
class ScrollXFlag(IntEnum):
    LEFT = -1
    RIGHT = 1
    STAY = 0

class PlayingView:
    # @profile
    def __init__(self, windowrect: Rect) -> None:
        self.WINDOW_WIDTH = windowrect.width
        self.HALFSCREENWIDTH = self.WINDOW_WIDTH/2
        self.INTERNAL_AND_WINDOW_HEIGHT_DIFF = 16
        self.PRINT_SCREEN_PIXEL_DIFF = 8
        self.WINDOW_HEIGHT = windowrect.height
        self.INTERNAL_HEIGHT = self.WINDOW_HEIGHT + self.INTERNAL_AND_WINDOW_HEIGHT_DIFF
        self.objmgr = ObjManager(StageEnum.CUTMAN, self.WINDOW_WIDTH, self.INTERNAL_HEIGHT)
        self.e_mgr = EnemyManager(self.objmgr.enemy_data,self.WINDOW_WIDTH)
        self.player = PlayerHandler(self.objmgr.start_point[0], self.objmgr.start_point[1],windowrect)
        self.screen_startX = (self.player.playerbox.x // self.WINDOW_WIDTH) * self.WINDOW_WIDTH
        self.screen_startY = (self.player.playerbox.y // self.INTERNAL_HEIGHT) * self.INTERNAL_HEIGHT + self.PRINT_SCREEN_PIXEL_DIFF
        #プレイヤー座標から表示区画の取得
        self.objmgr.preload_next_Yrange(self.player.playerbox.hitbox.center)
        self.e_mgr.capture_on_Y(self.objmgr.now_range)
        #スクリーン表示範囲内のオブジェクト抽出
        self.objmgr.get_objs_on_screen(self.screen_startX)

        self.SCROLLY_V = 4
        self.__is_scrolling_process:function = None
        self.__force_playermove:function = None

    @property
    def screen_endX(self) -> int:
        return self.screen_startX + self.WINDOW_WIDTH

    @property
    def screen_halfX(self) -> int:
        return self.screen_startX + self.HALFSCREENWIDTH

    def catch_input(self, eventsList: list[event.Event]):
        self.player.check_hit(self.e_mgr.on_screen_enemy)
        self.player.catch_input(eventsList, self.objmgr)

    def update_motion(self) -> None:
        self.player.update_motion(self.objmgr)

        prev_screen_startX = self.screen_startX
        if self.__is_scrollX(self.player.playerbox.hitbox, self.player.motion.vx):
            self.screen_startX += self.player.motion.vx
            #スクリーン表示範囲内のオブジェクト抽出※読み出し頻度を下げるため 1オブジェクト分のサイズの倍数の場合のみ実行する
            if self.screen_startX % 16 == 0 : self.objmgr.get_objs_on_screen(self.screen_startX)
        
        #画面内敵読み出し前処理
        if prev_screen_startX!=self.screen_startX:self.e_mgr.reflesh_enemy(self.screen_startX)

        #敵読み出し※読み出し頻度を下げるため 1オブジェクト分のサイズの倍数の場合のみ実行する
        if self.screen_startX % 16 == 0 : self.e_mgr.capture_on_screen(self.screen_startX)
        
        self.e_mgr.catch_player_location(self.player.playerbox.hitbox.center)
        self.e_mgr.catch_bullets(self.player.bullets)
        self.e_mgr.update()
        self.e_mgr.catch_terrain(self.objmgr.colidable_rects)

    def draw(self, surface) -> None:
        self.objmgr.draw(self.screen_startX, self.screen_startY, surface)
        self.player.draw(self.screen_startX, self.screen_startY, surface)
        self.e_mgr.draw(self.screen_startX,self.screen_startY,surface)

    def __is_scrollX(self, player_rect: Rect, capturevx: float) -> bool:
        __is_scrollleft = player_rect.centerx < self.screen_halfX and capturevx < 0 and self.screen_startX > self.objmgr.now_map_left
        __is_scrollright = player_rect.centerx > self.screen_halfX and capturevx > 0 and self.screen_endX < self.objmgr.now_map_right
        return __is_scrollleft or __is_scrollright

    def __scrollY_trigger(self, player_rect: Rect) -> ScrollYFlag:
        if player_rect.centery < self.screen_startY and self.objmgr.isexist_validrange(player_rect.topleft) and (self.player.state.isgrepladder):
            #上にスクロールする際は着地か梯子上り時のみスクロールを上げる
            return ScrollYFlag.UP
        elif player_rect.centery - self.screen_startY > self.WINDOW_HEIGHT and self.objmgr.isexist_validrange(player_rect.bottomleft):
            return ScrollYFlag.DOWN
        else:
            return ScrollYFlag.STAY

    #Y軸方向のスクロール処理 -> 引数で受け取ったScrollYFlagに応じたスクロール処理メソッドを返す
    def is_scrollY_process(self,now_state:ScrollYFlag,scroll_point:int) -> Callable[[ScrollYFlag,int],bool]:
        def process():
            if now_state == ScrollYFlag.DOWN and self.screen_startY < scroll_point:
                self.screen_startY += self.SCROLLY_V
                return True
            elif now_state == ScrollYFlag.UP and self.screen_startY > scroll_point:
                self.screen_startY -= self.SCROLLY_V
                return True
            else :
                self.screen_startY = scroll_point
                return False
        return process

    def scrollY_player_motion(self,now_state:ScrollYFlag):
        def process():
            if now_state == ScrollYFlag.DOWN and self.screen_startY > self.player.playerbox.y:
                self.player.playerbox.y = self.screen_startY 
            elif now_state == ScrollYFlag.UP and self.screen_startY + self.WINDOW_HEIGHT < self.player.playerbox.bottom:
                self.player.playerbox.bottom = self.screen_startY + self.WINDOW_HEIGHT + self.PRINT_SCREEN_PIXEL_DIFF / 2
            else :
                None
            self.player.force_update_motion()
        return process


    def is_auto_scrolling(self) -> bool:
        #プレイヤー座標からY軸スクロールするタイミングか否かをチェックする
        player_rect: Rect = self.player.playerbox.hitbox
        scrollingY_state = self.__scrollY_trigger(player_rect)
        
        #Y軸スクロールを行う場合の処理
        if (scrollingY_state != ScrollYFlag.STAY):
            if scrollingY_state == ScrollYFlag.UP:
                self.objmgr.preload_next_Yrange(player_rect.topleft)
            elif scrollingY_state == ScrollYFlag.DOWN:
                self.objmgr.preload_next_Yrange(player_rect.bottomleft)
            self.__is_scrolling_process = self.is_scrollY_process(scrollingY_state,self.objmgr.now_map_top + self.PRINT_SCREEN_PIXEL_DIFF)
            self.__force_playermove = self.scrollY_player_motion(scrollingY_state)
        
        #Y軸スクロールしない場合
        if self.__is_scrolling_process == None : return False

        is_processing_scroll = self.__is_scrolling_process()
        is_processing_moving = self.__force_playermove()

        if is_processing_scroll or is_processing_moving :
            #Y軸スクロール中
            eval_top = self.screen_startY - self.PRINT_SCREEN_PIXEL_DIFF
            if eval_top % self.PRINT_SCREEN_PIXEL_DIFF == 0: self.objmgr.get_objs_on_scrolling_Y(eval_top)
            return True 
        else: 
            #Y軸スクロール終了時
            self.__is_scrolling_process = None
            self.__force_playermove = None
            self.objmgr.get_objs_on_screen(self.screen_startX)
            self.e_mgr.capture_on_Y(self.objmgr.now_range)
            return False

    