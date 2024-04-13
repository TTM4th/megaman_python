from __future__ import annotations
import csv
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Generator
from pygame import Rect,Surface
from image import CutManTile

class StageEnum(Enum):
    TEST = 0
    CUTMAN = 1

class StageObject():
    def __init__(self, x: int, y: int, width: int) -> None:
        super().__init__()
        COLOR = (50, 127, 255)
        self.SIDELENGTH = width
        self._rect = Rect(x, y, self.SIDELENGTH, self.SIDELENGTH)
        self._image: Surface = Surface(
            self._rect.size)
        self._image.fill(COLOR)
        self._islandable = False
        self._iscolidable = False
        self._colidable_rect = None

    @property
    def image(self) -> Surface:
        return self._image

    @property
    def rect(self) -> Rect:
        return self._rect

    # 接触判定用Rect
    @property
    def colidable_rect(self) -> Rect:
        return self._colidable_rect

    # 接地可能フラグ
    @property
    def islandable(self) -> bool:
        return self._islandable

    # 接触可能フラグ
    @property
    def iscolidable(self) -> bool:
        return self._iscolidable

    def draw(self, screen_startx: int, screen_starty: int, surface: Surface) -> None:
        surface.blit(self._image, (self.rect.x-screen_startx,
                     self.rect.y - screen_starty))


class Block(StageObject):
    def __init__(self, x: int, y: int, sideLength: int, image: Surface) -> None:
        super().__init__(x, y, sideLength)
        self._image = image
        self._islandable = True
        self._iscolidable = True
        self._colidable_rect = self._rect


class Needle(StageObject):
    def __init__(self, x: int, y: int, sideLength: int, image: Surface) -> None:
        super().__init__(x, y, sideLength)
        self._image = image
        self._islandable = True
        self._iscolidable = False


class Shutter(StageObject):
    def __init__(self, x: int, y: int, sideLength: int, image: Surface) -> None:
        super().__init__(x, y, sideLength)
        self._image = image
        self._islandable = True
        self._iscolidable = False


class Laddar(StageObject):
    def __init__(self, x: int, y: int, sidelength: int, image: Surface) -> None:
        super().__init__(x, y, sidelength)
        self._image = image
        self.__istop = False

    @property
    def istop(self) -> bool:
        return self.__istop

    @istop.setter
    def istop(self, istop):
        self.__istop = istop
        self._islandable = self.__istop
        if self.__istop:
            self._colidable_rect = Rect(self.rect.topleft, (self.SIDELENGTH, 1))


class BackGround(StageObject):
    def __init__(self, x: int, y: int, sideLength: int, image: Surface) -> None:
        super().__init__(x, y, sideLength)
        self._image = image


class ObjManager():

    def __init__(self, stageenum: StageEnum, initscrwidth: int, initscrheight: int) -> None:
        
        self.SIDELENGTH: int = 16
        self.SCREENWIDTH: int = initscrwidth
        self.SCREENHEIGHT: int = initscrheight

        __m_loader = MapLoader(stageenum,self.SIDELENGTH)
        self.__bgobjs: set[StageObject] = __m_loader.bgobjs
        self.__fgobjs: set[StageObject] = __m_loader.fgobjs
        self.__e_data: set[EnemyData] = __m_loader.enemydata
        self.map_start_end: list[Rect] = __m_loader.get_start_end(self.SCREENWIDTH,self.SCREENHEIGHT)
        del __m_loader

        self.__firstplayerpoint: tuple[int, int] = tuple(map(lambda point : point * self.SIDELENGTH , MapConstant.START_SET[stageenum]))
        self.__stagemasterpoint: tuple[int, int] = tuple(map(lambda point : point * self.SIDELENGTH , MapConstant.MASTER_SET[stageenum]))

        self.__nowYrange_bgobjs: set[StageObject] = set()
        self.__nowYrange_fgobjs: set[StageObject] = set()
        self.__landable_rects: list[Rect] = []  # 着地可能なオブジェクト -> 接地はするが衝突はしない
        self.__colidable_rects: list[Rect] = []  # 接触可能なオブジェクト
        self.__laddar_rects: list[Rect] = []  # 梯子オブジェクト
        self.__topladdar_rects: list[Rect] = []  # 上端梯子オブジェクト
        self.__nowscreen_draw_bgobjs: set[StageObject] = set()
        self.__nowscreen_draw_fgobjs: set[StageObject] = set()

        #print(sorted(sorted(self.map_start_end,key = lambda rect : rect.left),key = lambda rect : rect.top))
    
    #第２引数で渡されたラムダ式に合致するStageObjectを第１引数から取得したStageObjectの集合から抽出する。
    def __filtering_objs_set(self,objs:set[StageObject],func:Callable[[StageObject],bool])->set[StageObject]:
        return {_ for _ in objs if func(_)}

    #引数で受け取ったStageObjectの集合から、地形情報を取得する。
    def __update_obj_rects(self, motherobjs: set[StageObject]) -> None:
        filter_process = lambda source , select_pred , where_pred: [select_pred(_) for _ in source if where_pred(_)]
        laddars = self.__filtering_objs_set(motherobjs, lambda x : isinstance(x, Laddar))
        self.__landable_rects = filter_process(motherobjs, lambda x : x.colidable_rect , lambda x : x.islandable)
        self.__colidable_rects = filter_process(motherobjs, lambda x : x.colidable_rect , lambda x : x.iscolidable)
        self.__laddar_rects = filter_process(laddars , lambda x : x.rect , lambda x : True)
        self.__topladdar_rects = filter_process(laddars , lambda x : x.rect , lambda x: x.istop)
        laddars.clear()

    #第２引数で受け取ったRectオブジェクト範囲中のオブジェクトを第１引数から抽出する。
    def __filtering_by_rect(self,objs:set[StageObject],view_range:Rect)->set[StageObject]:
        return self.__filtering_objs_set(objs, lambda obj : view_range.colliderect(obj.rect))

    #表示範囲内の描画用オブジェクトを取得する
    def __update_nowscreen_objs(self,view_range:Rect) -> None:
        self.__nowscreen_draw_bgobjs = (self.__filtering_by_rect(self.__nowscreen_draw_bgobjs, view_range) | self.__filtering_by_rect(self.__nowYrange_bgobjs, view_range))
        self.__nowscreen_draw_fgobjs = (self.__filtering_by_rect(self.__nowscreen_draw_fgobjs, view_range) | self.__filtering_by_rect(self.__nowYrange_fgobjs, view_range)) 

    #引数で受け取った表示開始X座標から表示するオブジェクトを取得する（X軸移動スクロール）
    def get_objs_on_screen(self, screen_startX: int) -> None:
        view_range = self.__now_range.copy()
        view_range.x = screen_startX-self.SIDELENGTH
        view_range.width = self.SCREENWIDTH + self.SIDELENGTH * 2 
        #self.__update_nowscreen_objs(Rect(screen_startX-self.SIDELENGTH , self.now_map_top,self.SCREENWIDTH + self.SIDELENGTH * 2 , self.SCREENHEIGHT))
        self.__update_nowscreen_objs(view_range)

    #スクロール中にスクロール表示するオブジェクトを取得する。
    def get_objs_on_scrolling_Y(self, now_load_topY: int) -> None:
        view_range = self.__now_range.copy()
        view_range.top = now_load_topY
        self.__update_nowscreen_objs(view_range)
    
    #プレイヤー位置情報から次のスクロール先区画を取得する。
    def __get_maprange_rect(self, player_point: tuple[int,int])->Generator[Rect,None,None]:
        return (_ for _ in self.map_start_end if _.inflate(0,-self.SIDELENGTH).collidepoint(player_point))

    #プレイヤー位置情報から次のスクロール先オブジェクトを取得する
    def preload_next_Yrange(self, player_point: tuple[int,int]) -> None:
        self.__now_range = next(self.__get_maprange_rect(player_point))
        self.__nowYrange_fgobjs = (self.__filtering_by_rect(self.__fgobjs, self.__now_range))
        search_range = self.__now_range.copy()
        search_range.height +=  self.SIDELENGTH
        #前スクリーンの梯子を余分に読み込ませて梯子を切らないために、底面座標は1オブジェクト分余分の高さを加えて読み込ませる
        now_range_set = self.__filtering_by_rect(self.__bgobjs, search_range)
        #前スクリーンから継続している壁を考慮して、別領域に存在する連続しているブロックオブジェクトだけ追加で読み込ませる
        add_range_set = {_ for range in (Rect(_.rect.left , self.now_map_top - self.SIDELENGTH * 3 , self.SIDELENGTH , self.SIDELENGTH * 3) 
                                for _ in now_range_set if isinstance(_,Block) and _.rect.top == self.now_map_top) 
                                for _ in self.__bgobjs if range.colliderect(_) }
        self.__nowYrange_bgobjs = (now_range_set | add_range_set)
        self.__update_obj_rects(self.__nowYrange_bgobjs)

    #次のスクロール先が存在するかチェックする。
    def isexist_validrange(self, player_point: tuple[int,int]) -> bool:
        return any(self.__get_maprange_rect(player_point))

    def draw(self, screen_startX: int, screen_startY: int, surface: Surface) -> None:
        for obj in self.__nowscreen_draw_bgobjs:
            obj.draw(screen_startX, screen_startY, surface) 
        for obj in self.__nowscreen_draw_fgobjs:
            obj.draw(screen_startX, screen_startY, surface)

    @property
    def landable_rects(self) -> list[Rect]:
        return self.__landable_rects

    @property
    def colidable_rects(self) -> list[Rect]:
        return self.__colidable_rects

    @property
    def laddar_rects(self) -> list[Rect]:
        return self.__laddar_rects

    @property
    def topladdar_rects(self) -> list[Rect]:
        return self.__topladdar_rects

    @property
    def start_point(self) -> tuple[int, int]:
        return self.__firstplayerpoint

    @property
    def now_map_right(self) -> int:
        return self.__now_range.right

    @property
    def now_map_left(self) -> int:
        return self.__now_range.left

    @property
    def now_map_top(self) -> int:
        return self.__now_range.top

    @property
    def now_map_bottom(self) -> int:
        return self.__now_range.bottom

    @property
    def now_range(self) -> Rect:
        return self.__now_range

    @property
    def enemy_data(self) -> set[EnemyData]:
        return self.__e_data

class MapLoader():
    def __init__(self,stageenum:StageEnum,t_sidelength:int) -> None:
        path = MapConstant.MAP_PATH[stageenum]
        self.i_master = MapConstant.TILE_SET[stageenum]()
        self.fgobjs:set[StageObject]=set()
        self.bgobjs:set[StageObject]=set()
        self.enemydata:set[EnemyData]=set()
        self.__loading(path,t_sidelength)

    def __loading(self,path:str,t_sidelength:int):
        with open(path, encoding='utf-8') as f:
            stageobj_targets:dict[str,set[StageObject]] = {'N': self.fgobjs, 'S': self.fgobjs,
                              'B': self.bgobjs, 'L': self.bgobjs, 'V': self.bgobjs}
            mapobj_selecter:dict[str,StageObject]  = {'N': Needle, 'S': Shutter,
                               'B': Block, 'L': Laddar, 'V': BackGround}
            rows = [_ for _ in csv.reader(f, delimiter="\t")]
            iscontact_lad = lambda eval_rect,anyone_rect :eval_rect.left == anyone_rect.left and eval_rect.top == anyone_rect.bottom

            for y in range(len(rows)):
                for x in range(len(rows[y])):
                    if not rows[y][x]:continue
                    ypoint = y*t_sidelength
                    xpoint = x*t_sidelength
                    value: str = rows[y][x]
                    for chip in value.split(','):
                        itemcode = chip[0]
                        if itemcode != 'E':
                            destinaton=stageobj_targets.get(itemcode)
                            obj = mapobj_selecter.get(itemcode)(
                                    xpoint, ypoint, t_sidelength, self.i_master.TILELIST[int(chip[1:])])
                            if isinstance(obj, Laddar):
                                obj.istop = any(anyone for anyone in destinaton if iscontact_lad(obj.rect,anyone.rect) and isinstance(anyone,BackGround))
                            destinaton.add(obj)
                        else :
                            self.enemydata.add(EnemyData(chip,xpoint,ypoint))
    
    #引数で受け取った１画面区画の高さと幅から、ステージ全体の表示区画を取得する
    def get_start_end(self,screen_width:int,screen_height:int):
        #1. ステージ全体の１画面区画の最も左上のオブジェクトの位置情報を１つずつ取得する
        isrange = lambda rect : rect.x % screen_width == 0 and rect.y % screen_height == 0
        all_topleft_obj = [obj.rect for obj in self.bgobjs if isrange(obj.rect)]
        #2. 1.で取得した左上位置情報のx,y座標から、ステージ上全ての１画面区画を１つずつ取得する。
        screens:list[Rect]=[Rect(rect.x,rect.y,screen_width,screen_height) for rect in all_topleft_obj]
        #3. 2.で取得した１画面区画は連続しておらず、X軸正方向に連続した場合のみ連結してX軸のみの任意スクロールが可能な表示区画を取得する。
        #setにしているのは同じY座標だが途切れているステージを想定して重複回避のためである。
        return [self.__get_unioned_rect(discreted_rect,screens) 
            for y in set(screen.top for screen in screens) 
                for discreted_rect in self.__get_first_rects(y,screens)]

    #上辺座標が第１引数のY座標になり、左辺が連続していない１画面分の区画を取得する
    def __get_first_rects(self,searchY:int,search_ranges:list[Rect]):
        filtered:list[Rect] = [rect for rect in search_ranges if rect.top == searchY]
        isdiscreted_func:bool = lambda eval_rect,eval_rects:not any(anyone_rect for anyone_rect in eval_rects
                                                            if eval_rect.left == anyone_rect.right)
        return [eval_rect for eval_rect in filtered if isdiscreted_func(eval_rect,filtered)]
        
    #第１引数で渡したRectオブジェクトとX軸正方向に連続するRectオブジェクトが存在すれば、連結したRectオブジェクトを返す
    def __get_unioned_rect(self,source_rect:Rect,search_ranges:list[Rect]):
        targets:Generator[Rect,None,None] = lambda eval_rect:(anyone_rect for anyone_rect in search_ranges 
                                                                if anyone_rect.left > eval_rect.left and 
                                                                eval_rect.top == anyone_rect.top and 
                                                                eval_rect.right == anyone_rect.left)
        while any(targets(source_rect)):
            source_rect.union_ip(next(targets(source_rect)))
        return source_rect

@dataclass(eq=True,frozen=True)
class EnemyData:
    key:str
    initx:int
    inity:int
    
class MapConstant():
    MAP_PATH = {StageEnum.TEST:"map/s_enemytest_emit_bullet.txt",StageEnum.CUTMAN:"map/s_cutman.txt"}
    START_SET = {StageEnum.TEST:(7,13),StageEnum.CUTMAN:(8,129)}
    MASTER_SET = {StageEnum.TEST:(0,15),StageEnum.CUTMAN:(203,56)}
    TILE_SET = {StageEnum.TEST:CutManTile,StageEnum.CUTMAN:CutManTile}