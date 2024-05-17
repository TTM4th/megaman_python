from __future__ import annotations

import pygame.transform
from pygame import Rect, Surface, locals
from pygame.event import Event
from megaman_python.image import CharaImageSource, Meter
from megaman_python.weapons import FireHandler, BulletObject
from megaman_python.stageobjects import ObjManager
from megaman_python.enemy import Enemy


class PlayerHandler:
    def __init__(self, initx: int, inity: int, windowrange: Rect) -> None:
        super().__init__()
        self.state = PlayerState()
        self.playerbox = PlayerBox(initx, inity)
        self.motion = MotionHandler()
        self.__player_timer = PlayerTimer(self.motion.V0MAXTIME)
        self.__graphic_handler = GraphicHandler()
        self.__control_dictionary = {
           locals.KEYDOWN: self.state.catch_keydown, locals.KEYUP: self.state.catch_keyup}
        self.__meter = Meter()
        self.image = self.__graphic_handler.standing_image(
            self.__player_timer.stand_timer, self.state)
        self.printrect = self.playerbox.printRect(self.state,self.image)
        self.__fire_handler = FireHandler(windowrange.width, windowrange.height)
        self.__hit_cancel_keys = {locals.K_UP,locals.K_DOWN,locals.K_LEFT,locals.K_RIGHT,locals.K_z,locals.K_x}

    #敵オブジェクトの接触チェック
    def check_hit(self,enemies:set[Enemy]):
        is_prevhit = self.state.ishit
        self.state.check_hit(self.playerbox,enemies)
        if is_prevhit != self.state.ishit:
            self.motion.reset_vx()
        if self.state.ishit:
            self.state.cancel_climbing()
            self.state.reset_pressLR_count()
            if not(is_prevhit):
                self.__player_timer.reset_falling()
                self.state.reset_releaseLR_count()
                self.state.CancelPressZKey()

        self.__meter.get_health(self.state.health)

    #入力チェック
    def catch_input(self, eventsList: list[Event], objs: ObjManager) -> None:
        # 更新前のチェック対象プレイヤーフラグを確認する
        is_prevstand = self.state.isstand
        is_prevfalling = self.state.isjump or self.state.inair
        is_prevgreplad = self.state.isgrepladder
        is_prevLR = self.state.ispressed_LR

        # イベントキューからキーボードやマウスの動きを取得
        for _ in filter(lambda x: x.type == locals.KEYDOWN or x.type == locals.KEYUP, eventsList):
            #のけぞり中は上下左右ZXキーの押下イベントはキャッチしない
            if self.state.ishit and any(key for key in self.__hit_cancel_keys 
                if _.key == key and _.type == locals.KEYDOWN): continue 
            #操作受付
            self.__control_dictionary[_.type](_.key)

        # 現在のプレイヤー状態を取得
        self.state.get_direction()
        self.state.check_grep_ladder(self.playerbox, objs.laddar_rects)
        self.state.check_land_or_crawl_laddar(
            self.playerbox, objs.topladdar_rects)
        self.state.check_landing(self.playerbox, objs.landable_rects)
        self.state.ispositve_Y = (self.motion.vy >= 0)
        self.state.check_fire(self.__fire_handler.ismax_bullet)

        # 入力イベント捕捉後直立じゃない場合
        if is_prevstand and not(self.state.isstand):
            self.__player_timer.reset_standing()
        # 入力イベント捕捉後空中じゃない場合（空中処理のリセット)
        if is_prevfalling and not(self.state.isjump or self.state.inair):
            self.__player_timer.reset_falling()
        # 入力イベント捕捉後梯子掴み状態でない場合
        if is_prevgreplad and not(self.state.isgrepladder):
            self.__player_timer.reset_climbing()
        # 入力イベント捕捉後左右キー押下じゃない場合
        if is_prevLR and not(self.state.ispressed_LR):
            self.state.reset_pressLR_count()
            self.__player_timer.reset_running()
            self.motion.reset_vx()
        elif not(is_prevLR) and self.state.ispressed_LR:
            self.state.reset_releaseLR_count()

    #自動スクロール開始時にプレイヤー状態を強制アップデートしたい処理を実行するメソッド
    def force_update_motion(self) -> None:
        self.state.cancel_in_scroll()
        if self.state.isgrepladder:
            self.__player_timer.count_climbing()
            self.image = self.__graphic_handler.climbing_image(self.__player_timer.climb_timer, self.state)
            self.refresh_location()

    def refresh_location(self) -> None:
        self.printrect = self.playerbox.printRect(self.state,self.image)

    # 自キャラ位置と描画画像の更新
    def update_motion(self, objs: ObjManager) -> None:
        if self.state.iscrawling:
            if self.state.isstaying_crawl():
                self.image = self.__graphic_handler.crawring_image()
            else:
                self.motion.update_aftercrawling(objs, self.state, self.playerbox)
                self.image = self.__graphic_handler.climbing_image(self.__player_timer.climb_timer, self.state)
        elif self.state.isgrepladder:
            if self.state.ispressed_UPDOWN:self.__player_timer.count_climbing()
            self.image = self.__graphic_handler.climbing_image(self.__player_timer.climb_timer, self.state)
            self.motion.calc_laddar_vy(self.state)
            self.motion.update_climbing_y(objs, self.state, self.playerbox)
        else:
            if self.state.isstand:
                self.__player_timer.count_standing()
                self.image = self.__graphic_handler.standing_image(self.__player_timer.stand_timer, self.state)

            if self.state.inair or self.state.isjump:
                self.image = self.__graphic_handler.jump_image(self.state)
                if self.state.isjump:  # ジャンプ
                    self.__player_timer.count_jumping()
                else:  # 落下
                    self.__player_timer.count_in_air(self.state.ispositve_Y)
                self.motion.calc_fall_vy(self.__player_timer, self.state)

            if self.state.ispressed_LR:
                self.state.count_pressLR_time()  # 左右押下時間判定
                self.motion.calc_vx(self.state)
            else:
                self.state.count_releaseLR_time()

            if self.state.isstepping:
                self.image = self.__graphic_handler.stepping_image(self.state)
            elif self.state.isrunning:
                self.__player_timer.count_running()
                self.image = self.__graphic_handler.running_image(self.__player_timer.run_timer, self.state)
            elif self.state.ishit:
                self.motion.knock_back(self.state)
                self.image = self.__graphic_handler.damaged_image(self.state)

            self.motion.update_y(objs, self.state, self.playerbox)
            self.motion.update_x(objs, self.state, self.playerbox)

        self.refresh_location()

        # バスター発射ボタンの状態検知
        if self.state.istrigger:
            self.__fire_handler.fire(self.printrect, self.state.isright)
            self.state.cancel_trigger()
        if self.__fire_handler.isexist_bullet:
            self.__fire_handler.update()


    # 画面内への描画
    def draw(self, screen_adjust_x: int, screen_adjust_y: int, surface: Surface) -> None:
        self.__meter.draw(surface)
        self.__fire_handler.draw(screen_adjust_x, screen_adjust_y, surface)

        draw_px = self.printrect.x-screen_adjust_x
        draw_py = self.printrect.y-screen_adjust_y
        if self.state.ishit:
            surface.blit(self.__graphic_handler.hit_effect_large(self.state),(draw_px+1,draw_py-3))
            s_effect = self.__graphic_handler.hit_effect_small(self.state)
            if s_effect!=None: surface.blit(s_effect,(draw_px,draw_py-8))
        if self.state.isinvisible and self.state.isblink : return
        surface.blit(self.image, (draw_px,draw_py))

    @property
    def bullets(self) -> list[BulletObject]:
        return self.__fire_handler.bullets

class PlayerBox:
    def __init__(self, x: int, y: int) -> None:
        self.COLIDESIZE = (16, 24)
        self.__hitbox = Rect((x,y),self.COLIDESIZE)
        self.LADDARMARGIN = 10
        self.LANDSIZE_SIDE = 16
        self.__landbox = Rect((self.__hitbox.x,self.__hitbox.y+self.COLIDESIZE[1]-self.LANDSIZE_SIDE),self.COLIDESIZE)

    # 衝突判定用Rectオブジェクト
    @property
    def hitbox(self) -> Rect:
        return self.__hitbox

    @property
    def x(self) -> float:
        return self.__hitbox.x

    @property
    def y(self) -> float:
        return self.__hitbox.y

    @x.setter
    def x(self,x) -> float:
        self.__hitbox.x = x

    @y.setter
    def y(self,y) -> float:
        self.__hitbox.y = y

    # 位置情報タプル
    @property
    def point(self) -> tuple[int, int]:
        return self.hitbox.topleft

    @property
    def bottom(self) -> float:
        return self.__hitbox.bottom

    @bottom.setter
    def bottom(self, bottom) -> float:
        self.__hitbox.bottom = bottom

    @property
    def landbox(self) -> Rect:
        #return Rect(self.x,self.y+(self.COLIDESIZE[1]-self.LANDSIZE_SIDE),self.LANDSIZE_SIDE,self.LANDSIZE_SIDE)
        self.__landbox.topleft = self.__hitbox.topleft
        return self.__landbox

    # 出力用Rectオブジェクト
    def printRect(self, flags: PlayerState , print_image:Surface) -> Rect:
        if flags.isgrepladder:
            rtnrect = self.hitbox.copy()
        elif flags.inair:
            rtnrect = self.hitbox.inflate(10,0)
        elif flags.ishit:
            rtnrect = self.hitbox.inflate(10,0)
        else:
            rtnrect = self.hitbox.inflate(5, 0)
        if not(flags.isright):
            rtnrect.move_ip(-(print_image.get_width()-rtnrect.width),0)
        return rtnrect

    
    # 梯子接触判定用Rectオブジェクト todo:上下キーの押下状況で上下にいくつかずらすことも考える（登り切った後に一瞬だけ登りパターンが表示されるバグ回避のため）
    @property
    def ladderrect(self) -> Rect:
        rtnrect = self.hitbox.inflate(-14, -self.LADDARMARGIN)
        rtnrect.move_ip(0, self.LADDARMARGIN/2)
        return rtnrect

    # 受け取った引数のX座標に強制移動する
    def force_adjust_ladder_x(self, x: int) -> None:
        if self.x != x: self.x = x

    # 受け取った引数のy座標に強制移動する
    def force_adjust_ladder_y(self, y: int) -> None:
        if self.y != y: self.y = y


# プレイヤーキャラクタ移動ロジッククラス
class MotionHandler:
    def __init__(self) -> None:
        self.__MAXJUMPHEIGHT = 16 * 3 + 4
        self.V0MAXTIME = 20
        self.__MOVEXVELOCITY = 1
        self.__g = self.__MAXJUMPHEIGHT * 2 * ((self.V0MAXTIME) ** -2)
        self.__v0max = self.V0MAXTIME * self.__g
        self.__vy = 0
        self.__vx = 0

    # X軸移動速度

    @property
    def vx(self) -> int:
        return self.__vx

    # Y軸移動速度
    @property
    def vy(self) -> int:
        return self.__vy

    # Y軸移動速度の初期化処理
    def reset_vy(self) -> None:
        self.__vy = 0

    # 空中のY軸移動速度計算ルーチン
    def calc_fall_vy(self, timer: PlayerTimer, state: PlayerState) -> None:
        time: int = 0
        diff: int = 0
        if state.isjump:
            time = timer.jump_timer
            diff = -self.__v0max
        elif state.inair:
            time = timer.air_timer
        self.__vy = diff + self.__g * time

    # 左右キー押下時のX軸移動速度計算ルーチン
    def calc_vx(self, state: PlayerState) -> None:
        if state.isright:
            self.__vx = self.__MOVEXVELOCITY
        else:
            self.__vx = -self.__MOVEXVELOCITY

    def knock_back(self,state: PlayerState) -> None:
        if state.isright:
            self.__vx = -self.__MOVEXVELOCITY * state.isblink
        else:
            self.__vx = self.__MOVEXVELOCITY * state.isblink

    # 左右キー非押下時のX軸移動速度初期化ルーチン
    def reset_vx(self) -> None:
        self.__vx = 0

    # 検出した梯子昇降移動のフラグに応じて梯子昇降移動量を計算する
    def calc_laddar_vy(self, flags: PlayerState) -> None:
        if flags.isclimb_up:
            self.__vy = -1
        elif flags.isclimb_down:
            self.__vy = 1
        else:
            self.__vy = 0

    # ジャンプ、滞空時のY軸移動量を引数で受けたプレイヤーオブジェクトに反映させる
    def update_y(self, objs: ObjManager, nowstate: PlayerState, player: PlayerBox) -> None:
        player.y += self.__vy

        if nowstate.ispositve_Y:
            eval_objRects:list[Rect] = objs.landable_rects 
            eval_playerbox:Rect = player.landbox
        else:
            eval_objRects:list[Rect] = objs.colidable_rects
            eval_playerbox:Rect = player.hitbox

        if nowstate.isexist_colidobjs(eval_playerbox, eval_objRects):
            obj: Rect = next(_ for _ in eval_objRects if _.colliderect(eval_playerbox))
            nowstate.CancelPressZKey()
            if nowstate.ispositve_Y:
                player.bottom = obj.top
            else:
                player.y = obj.bottom

    # X軸移動量を引数で受けたプレイヤーオブジェクトに反映させる
    def update_x(self, objs: ObjManager, nowstate: PlayerState, player: PlayerBox) -> None:
        tmp = player.hitbox.move(self.__vx, 0)
        if nowstate.isexist_colidobjs(tmp, objs.colidable_rects) or tmp.left <= objs.now_map_left or tmp.right >= objs.now_map_right:
            self.reset_vx()
        else:
            player.x += self.__vx

    # 梯子這い上がり時のY軸移動量を引数で受けたプレイヤーオブジェクトに反映させる
    def update_aftercrawling(self, colidobjs: ObjManager, nowstate: PlayerState, player: PlayerBox) -> None:
        srch = next(_ for _ in colidobjs.topladdar_rects if _.colliderect(
            player.ladderrect))
        if nowstate.isclimb_up:
            player.bottom = srch.top
            nowstate.cancel_climbing()
        elif nowstate.isclimb_down:
            player.y = srch.top + int(nowstate.isclimb_down)
        else :
            return
        self.reset_vy()

    # 梯子昇降移動時のY軸移動量を引数で受けたプレイヤーオブジェクトに反映させる
    def update_climbing_y(self, colidobjs: ObjManager, nowstate: PlayerState, player: PlayerBox) -> None:
        player.y += self.__vy
        if any(_ for _ in colidobjs.colidable_rects if nowstate.iscontact_bottom(player.hitbox, _)):
            nowstate.cancel_climbing()
        elif any(_ for _ in colidobjs.colidable_rects if player.hitbox.colliderect(_)):
            blk = next(
                _ for _ in colidobjs.colidable_rects if player.hitbox.colliderect(_))
            player.force_adjust_ladder_y(blk.bottom)
        elif any(_ for _ in colidobjs.topladdar_rects if player.ladderrect.colliderect(_)
                 and player.hitbox.top <= _.top):
            nowstate.force_crawling()
        else :
            return
        self.reset_vy()

# プレイヤーイメージの表示ロジッククラス
class GraphicHandler:
    def __init__(self) -> None:
        self.__IMAGE = CharaImageSource()
        self.__RUNPIC: list[Surface] = [
            self.__IMAGE.RUN1, self.__IMAGE.RUN2, self.__IMAGE.RUN3]
        self.__RUNEACH = 8
        self.__RUNPATTERNCOUNT = len(self.__RUNPIC) + 1  # 中割フレーム使いまわしのため+1
        self.__FIRERUNPICS: list[Surface] = [
            self.__IMAGE.FIRERUN1, self.__IMAGE.FIRERUN2, self.__IMAGE.FIRERUN3]
        self.__HOLDRUNPICS: list[Surface] = [
            self.__IMAGE.HOLDRUN1, self.__IMAGE.HOLDRUN2, self.__IMAGE.HOLDRUN3]
        self.__STANDPICS: list[Surface] = [
            self.__IMAGE.STAND, self.__IMAGE.STANDBLINK]
        self.__HOLDSTANDPICS: list[Surface] = [
            self.__IMAGE.HOLDSTAND, self.__IMAGE.HOLDSTANDBLINK]
        self.__WARPLANDPICS: list[Surface] = [
            self.__IMAGE.WARPLAND1, self.__IMAGE.WARPLAND2]
        self.__WARPEACH = 15
        self.__WARPPATTERNCOUNT = len(self.__WARPLANDPICS)
        self.__HIT_EFFECT_LARGE = self.__IMAGE.HIT_EFFECT_LARGE
        self.__HIT_EFFECT_SMALLS:list[Surface] = [self.__IMAGE.HIT_EFFECT_SMALL1,self.__IMAGE.HIT_EFFECT_SMALL2,self.__IMAGE.HIT_EFFECT_SMALL3]

    # 走行中の画像を取得する
    def running_image(self, run_timer: int, flags: PlayerState) -> Surface:
        frameindex = (run_timer//self.__RUNEACH) % self.__RUNPATTERNCOUNT
        if frameindex == 3:
            frameindex = 1
        _ = self.__RUNPIC[frameindex]
        if flags.isfire == True:
            _ = self.__FIRERUNPICS[frameindex]
        if flags.ishold == True:
            _ = self.__HOLDRUNPICS[frameindex]
        return self.__GetflippedImage(_, flags.isright)

    # 直立時の画像を取得する
    def standing_image(self, stand_timer: int, flags: PlayerState) -> Surface:
        frameindex = (lambda x: 1 if x // 6 == 18 else 0)(stand_timer)
        if flags.isfire == True and flags.ishold == True:
            _ = self.__IMAGE.THROW
        elif flags.isfire == True:
            _ = self.__IMAGE.FIRE
        elif flags.ishold == True:
            _ = self.__HOLDSTANDPICS[frameindex]
        else:
            _ = self.__STANDPICS[frameindex]
        return self.__GetflippedImage(_, flags.isright)

    # ワープ用の画像を取得する
    def warping_image(self, warp_timer: int, flags: PlayerState) -> Surface:
        if flags.island == False:
            return self.__IMAGE.WARP
        frameindex = (warp_timer//self.__WARPEACH) % self.__WARPPATTERNCOUNT
        return self.__WARPLANDPICS[frameindex]

    # ジャンプ中の画像を取得する
    def jump_image(self, flags: PlayerState) -> Surface:
        if flags.ishold == True and flags.isfire == True:
            _ = self.__IMAGE.JUMPTHROW
        elif flags.ishold == True:
            _ = self.__IMAGE.HOLDJUMP
        elif flags.isfire == True:
            _ = self.__IMAGE.JUMPFIRE
        else:
            _ = self.__IMAGE.JUMP
        return self.__GetflippedImage(_, flags.isright)

    # 踏み込み状態の画像を取得する
    def stepping_image(self, flags: PlayerState) -> Surface:
        if flags.ishold == True:
            _ = self.__IMAGE.HOLDSTEPPING
        else:
            _ = self.__IMAGE.STEPPING
        return self.__GetflippedImage(_, flags.isright)

    # ハシゴ昇降状態の画像を取得する
    def climbing_image(self, climb_timer: int, flags: PlayerState) -> Surface:
        if flags.ishold and flags.isfire:
            return self.__GetflippedImage(self.__IMAGE.CLIMBINGTHROW, flags.isright)
        if flags.isfire:
            return self.__GetflippedImage(self.__IMAGE.CLIMBINGFIRE, flags.isright)
        return self.__IMAGE.CLIMBING if (climb_timer // 10) % 2 == 1 else pygame.transform.flip(self.__IMAGE.CLIMBING, True , False)

    # 梯子這い上がり時の画像を取得する
    def crawring_image(self) -> Surface:
        return self.__IMAGE.CRAWLING

    def damaged_image(self,flags: PlayerState) -> Surface:
        return self.__GetflippedImage(self.__IMAGE.DAMAGED, flags.isright)

    def hit_effect_small(self,flags: PlayerState) -> Surface:
        if flags.hittimer < 24 : return self.__GetflippedImage(self.__HIT_EFFECT_SMALLS[flags.hittimer//8], flags.isright)
        else : return None

    def hit_effect_large(self,flags:PlayerState) -> Surface:
        return self.__GetflippedImage(self.__HIT_EFFECT_LARGE, flags.isright)

    # 操作時の方向フラグにより左右反転した画像を表示する
    def __GetflippedImage(self, image: Surface, isright: bool) -> Surface:
        return image if isright else pygame.transform.flip(image, not(isright), False)

# プレイヤーキャラクターの各状態タイマーをカウントするロジッククラス
class PlayerTimer:
    def __init__(self, v0maxtime: int) -> None:
        self.__standtimer = 0
        self.__jumptimer = 0
        self.__runtimer = 0
        self.__airtimer = 0
        self.__v0maxtime = v0maxtime
        self.__STANDMAXTIME = 180
        self.__RUNMAXTIME = 32
        self.__climbtimer = 0
        self.__CLIMBMAXFRAME = 20
        self.__MAXFALLINGTIMER = 42

    # 直立時に直立用タイマーカウントを行うロジック
    def count_standing(self) -> None:
        self.__standtimer += 1
        if self.__standtimer > self.__STANDMAXTIME:
            self.__standtimer -= self.__STANDMAXTIME

    # 直立状態が解除された際に直立用タイマーをリセットするロジック
    def reset_standing(self) -> None:
        self.__standtimer = 0

    # ジャンプ時にジャンプ用タイマーカウントを行うロジック
    def count_jumping(self) -> None:
        self.__jumptimer += 1
        self.__airtimer = 0

    # ジャンプキー非押下時の空中用タイマーカウントを行うロジック
    def count_in_air(self, isPositiveY: bool) -> None:
        # ジャンプした後の滞空状態か否かを判別して、落下中にZキーを離した場合はタイマー引継処理を行う
        if isPositiveY and self.__airtimer == 0 and self.__jumptimer > 0:self.__airtimer = self.__jumptimer - self.__v0maxtime
        if self.__airtimer < self.__MAXFALLINGTIMER :self.__airtimer += 1
        if self.__jumptimer > 0 : self.__jumptimer = 0

    # ジャンプ時および空中状態の終了時にジャンプ用および空中用タイマーをリセットするロジック
    def reset_falling(self) -> None:
        self.__jumptimer = 0
        self.__airtimer = 0

    # 走行時に走行用タイマーカウントを行うロジック
    def count_running(self) -> None:
        self.__runtimer += 1
        if self.__runtimer > self.__RUNMAXTIME:self.__runtimer -= self.__RUNMAXTIME

    # 走行終了時に走行用タイマーをリセットするロジック
    def reset_running(self) -> None:
        self.__runtimer = 0

    # 梯子昇降時にタイマーカウントを行うロジック
    def count_climbing(self) -> None:
        self.__climbtimer += 1
        if self.__climbtimer > self.__CLIMBMAXFRAME:self.__climbtimer -= self.__CLIMBMAXFRAME

    # 梯子昇降解除時にタイマーをリセットするロジック
    def reset_climbing(self) -> None:
        self.__climbtimer = 0
        self.__jumptimer = 0
        self.__airtimer = 0

    @property
    def stand_timer(self) -> int:
        return self.__standtimer

    @property
    def run_timer(self) -> int:
        return self.__runtimer

    @property
    def jump_timer(self) -> int:
        return self.__jumptimer

    @property
    def air_timer(self) -> int:
        return self.__airtimer

    @property
    def climb_timer(self) -> int:
        return self.__climbtimer

class keyInputState:
    def __init__(self) -> None:
        self._ispressed_R = False
        self._ispressed_L = False
        self._LR_presstime = 0
        self.__STEPCOUNT = 6
        self._Issteppingfunc = lambda x: True if x < self.__STEPCOUNT else False
        self._ispressed_Z = False
        self._ispressed_X = False
        self._ispressed_Up = False
        self._ispressed_down = False
        self._isright = True
        self._LR_releasetime = 0

    # 押下した操作用キー情報からクラス内のフラグを更新する
    def catch_keydown(self, downkey: int) -> None:
        if downkey == locals.K_RIGHT:
            self._ispressed_R = True
            self._ispressed_L = False
        elif downkey == locals.K_LEFT:
            self._ispressed_L = True
            self._ispressed_R = False
        elif downkey == locals.K_z:self._ispressed_Z = True
        elif downkey == locals.K_x:self._ispressed_X = True
        elif downkey == locals.K_DOWN:self._ispressed_down = True
        elif downkey == locals.K_UP:self._ispressed_Up = True

    # 押下解除した操作用キー情報からクラス内のフラグを更新する
    def catch_keyup(self, upkey: int) -> None:
        if upkey == locals.K_RIGHT:self._ispressed_R = False
        elif upkey == locals.K_LEFT:self._ispressed_L = False
        elif upkey == locals.K_z:self._ispressed_Z = False
        elif upkey == locals.K_x:self._ispressed_X = False
        elif upkey == locals.K_DOWN:self._ispressed_down = False
        elif upkey == locals.K_UP:self._ispressed_Up = False

    # 左右カーソルキーの押下時間カウントをリセットするメソッド
    def reset_pressLR_count(self) -> None:
        if self._LR_presstime > 0:self._LR_presstime = 0

    # 左右カーソルキーの開放時間カウントをリセットするメソッド
    def reset_releaseLR_count(self) -> None:
        if self._LR_releasetime > 0:self._LR_releasetime = 0

    # バスター射出後の入力をキャンセルする
    def cancel_trigger(self) -> None:
        self._ispressed_X = False

    # 進行方向は右を向いているか
    @property
    def isright(self) -> bool:
        return self._isright

    # バスター発射ボタンを押下したか否か
    @property
    def istrigger(self) -> bool:
        return self._ispressed_X

    # 上下ボタン押下中か否か
    @property
    def ispressed_UPDOWN(self) -> bool:
        return self._ispressed_Up or self._ispressed_down

class PlayerState(keyInputState):

    def __init__(self) -> None:
        super().__init__()
        self.__island = True
        self.__isfire = False
        self.ishold = False
        self.__isjump = False
        self.__isgrepladder = False
        self.__iscrawling = False
        self.__clawltimer = 0
        self.__CLAWLMAXTIME = 6
        # 滞空時の進行方向は正の方向（落下）か否か
        self.ispositve_Y = True
        self.__fireposetimer = 0
        self.__FIREMAXTIME = 15
        self.__MAXHEALTH = 28
        self.health = self.__MAXHEALTH
        self.__INVISIBLETIME = 120
        self.__HITTIME = 60
        self.hittimer = 0

    # 地上に梯子がある場合の昇降チェック
    def check_land_or_crawl_laddar(self, player: PlayerBox, topladderrects: list[Rect]) -> None:
        if any(_ for _ in topladderrects if self.iscontact_bottom(
                player.ladderrect, _)) and self.island and self._ispressed_down:
            self.__iscrawling = True
            self.__isgrepladder = True
            self._ispressed_L = False
            self._ispressed_R = False

        if self.iscrawling:
            obj = next(_ for _ in topladderrects if player.hitbox.colliderect(_)
                       or self.iscontact_bottom(player.ladderrect, _))
            player.force_adjust_ladder_x(obj.x)
            player.force_adjust_ladder_y(obj.y - 10)
            if self.isfire:
                self.__iscrawling = False

    # 梯子昇降可能か否かのチェック
    def check_grep_ladder(self, player: PlayerBox, ladderrects: list[Rect]) -> None:
        onladdar = self.isexist_colidobjs(player.ladderrect, ladderrects)
        isgrepmotion = (onladdar and self.island and self._ispressed_Up) or (onladdar and self.inair and self.ispressed_UPDOWN)
        if isgrepmotion:
            self.__isgrepladder = True
            self._ispressed_L = False
            self._ispressed_R = False
            player.force_adjust_ladder_x(next(_ for _ in ladderrects if player.ladderrect.colliderect(_)).x)
        elif self.isgrepladder:
            if self._ispressed_Z:
                self.__isgrepladder = False
                self._ispressed_Z = False
                self.__island = False
                if self.__iscrawling: self.__iscrawling = False
            else:
                self.__isgrepladder = onladdar

    # 第１引数で受け取った自キャラRectが、第2引数の物体リストのどれかに接触するかをチェックする
    def isexist_colidobjs(self, player: Rect, checkObjs: list[Rect]) -> bool:
        return any(_ for _ in checkObjs if player.colliderect(_))

    # 第１引数で受け取った自キャラRectから着地情報を更新する
    def check_landing(self, player: PlayerBox, landableRects: list[Rect]) -> None:
        self.__island = any(
            _ for _ in landableRects if self.iscontact_bottom(player.hitbox, _)) and not(self.isgrepladder)

        if self.island and not(self.isgrepladder):
            self.__isjump = self._ispressed_Z
            self.__island = not(self.isjump)
        else:
            if not(self._ispressed_Z) or self.isgrepladder:
                self.__isjump = False
            if not(self.isjump):
                self._ispressed_Z = False

    def iscontact_bottom(self, playerrect: Rect, landrect: Rect) -> bool:
        return playerrect.bottom == landrect.top and not(playerrect.right <= landrect.left or playerrect.left >= landrect.right)

    # 発射体制か否かのチェック
    def check_fire(self, ismaxbullet: bool) -> None:
        if self.istrigger:
            self.__isfire = not(ismaxbullet)
        if self.__isfire and not(self.istrigger):
            self.__fireposetimer += 1
        else:
            self.__fireposetimer = 0
        if self.__fireposetimer > self.__FIREMAXTIME:
            self.__isfire = False
            self.__fireposetimer = 0

    # 梯子這い上がり中に上下押下時間から這い上がり更新された這い上がり状態フラグを返す
    # この関数を実行した際はIsCrawlingプロパティも更新される
    def isstaying_crawl(self) -> bool:
        if self.iscrawling and self.ispressed_UPDOWN:
            self.__clawltimer += 1
        else:
            self.__clawltimer = 0
        if self.__clawltimer > self.__CLAWLMAXTIME:
            self.__iscrawling = False
            self.__clawltimer = 0
        return self.__iscrawling

    #敵との接触をチェックする
    def check_hit(self,player: PlayerBox, enemyobjs:set[Enemy])->None:
        if not(self.isinvisible) and any(_ for _ in enemyobjs if player.hitbox.colliderect(_.hitrect) and _.live ):
            dmg = next(_ for _ in enemyobjs if player.hitbox.colliderect(_.hitrect)).attack
            self.health -= dmg
            self.hittimer = 1
            #print(self.health,dmg)
        elif self.isinvisible:
            self.hittimer += 1
        if self.hittimer >= self.__INVISIBLETIME : self.hittimer = 0

    @property
    # 空中に存在するか否かのフラグ
    def inair(self) -> bool:
        return not(self.island)

    @property
    # ジャンプ状態かどうか
    def isjump(self) -> bool:
        return self.__isjump

    @property
    # 着地状態かどうか
    def island(self) -> bool:
        return self.__island

    # 梯子を掴んでいるか否か
    @property
    def isgrepladder(self) -> bool:
        return self.__isgrepladder

    # 梯子昇降状態のフラグを強制的に解除する
    def cancel_climbing(self) -> None:
        self._ispressed_Up = False
        self._ispressed_down = False
        self.__isgrepladder = False
        #2022/10/19被弾時の這い上がりキャンセルをここに盛り込む→被弾後強制的に梯子上に着地する
        self.__iscrawling = False

    # 梯子這い上がり状態に強制的に設定する
    def force_crawling(self) -> None:
        self.__iscrawling = True

    # 接地・頭上接触時のZキー押下を強制解除する処理
    def CancelPressZKey(self) -> None:
        self._ispressed_Z = False
        self.__isjump = False

    #画面強制スクロール時にプレイヤーの動作を強制解除する処理
    def cancel_in_scroll(self) -> None:
        self._ispressed_X = False
        self.__isfire = False

    # 左右カーソルキーの押下時間をカウントするメソッド
    def count_pressLR_time(self) -> None:
        # _Issteppingが真を返したらカウンタに+1、そうでなければ0を足す（※タイマオーバーフローを防ぐため）
        self._LR_presstime += int(self._Issteppingfunc(self._LR_presstime)
                                  ) * int(self.ispressed_LR)

    def count_releaseLR_time(self) -> None:
        # _Issteppingが真を返したらカウンタに+1、そうでなければ0を足す（※タイマオーバーフローを防ぐため）
        self._LR_releasetime += int(self._Issteppingfunc(
            self._LR_releasetime)) * int(not(self.ispressed_LR))

    #プレイヤーの方向情報を更新する処理
    def get_direction(self) -> None:
        if self.ishit: return
        if self._ispressed_R :self._isright = True
        elif self._ispressed_L : self._isright = False

    # 左右キー押下中か否か
    @property
    def ispressed_LR(self) -> bool:
        return (self._ispressed_L or self._ispressed_R) and not(self.ishit)

    # バスター発射状態か否か
    @property
    def isfire(self) -> bool:
        return self.__isfire

    # 投擲してるか否か
    @property
    def isthrow(self) -> bool:
        return self.isfire and self.ishold

    # 地面上に静止してるか否か
    @property
    def isstand(self) -> bool:
        return not(self.ispressed_LR) and self.island

    # 這い上がり状態か否か
    @property
    def iscrawling(self) -> bool:
        return self.__iscrawling

    # 踏み込み状態であるか否か
    @property
    def isstepping(self) -> bool:
        if self.ispressed_LR: return self._Issteppingfunc(self._LR_presstime) and self.island
        else: return self._Issteppingfunc(self._LR_releasetime) and self.island

    # 走り込み状態か否か
    @property
    def isrunning(self) -> bool:
        return not(self._Issteppingfunc(self._LR_presstime)) and self.island

    # 梯子上り状態か否か
    @property
    def isclimb_up(self) -> bool:
        return self.__isgrepladder and self._ispressed_Up and not(self.isfire)

    # 梯子降り状態か否か
    @property
    def isclimb_down(self) -> bool:
        return self.__isgrepladder and self._ispressed_down and not(self.isfire)

    #被弾のけぞり状態か
    @property
    def ishit(self) -> bool:
        return self.hittimer > 0 and self.hittimer < self.__HITTIME

    #無敵状態か
    @property
    def isinvisible(self) -> bool:
        return self.hittimer > 0 and self.hittimer < self.__INVISIBLETIME

    #表示しないタイミングか
    @property
    def isblink(self) -> bool:
        return self.hittimer % 3 == 0 

    #生存中か
    @property
    def islive(self) -> bool:
        return self.health > 0