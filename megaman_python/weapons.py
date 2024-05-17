from __future__ import annotations
from pygame import Rect, Surface
from .image import BusterBulletImage

class FireHandler:
    def __init__(self, scrwidth: int, scrheight: int) -> None:
        self.bulletImage = BusterBulletImage().BUSTERBULLET
        self.__MAXBULLETS = 3
        self._bullets: list[BulletObject] = []*self.__MAXBULLETS
        self.SCREENWIDTH = scrwidth
        self.SCREENHEIGHT = scrheight

    @property
    def isexist_bullet(self) -> bool:
        return any(self._bullets)

    @property
    def ismax_bullet(self) -> bool:
        return len(self._bullets) >= self.__MAXBULLETS

    @property
    def bullets(self) -> list[BulletObject]:
        return self._bullets

    def fire(self, nowplayerLoc: Rect, isright: bool) -> None:
        if not(self.isexist_bullet) or not(self.ismax_bullet):
            self._bullets.append(BulletObject(
                nowplayerLoc, isright, self.bulletImage))
            # todo:ここに発射時の音を鳴らす処理を入れる

    def update(self) -> None:
        for _ in self._bullets:
            _.update()

    def draw(self, screen_adjust_x: int, screen_adjust_y: int, screen: Surface) -> None:
        for bullet in self._bullets:
            if self.isprint_range(bullet, screen_adjust_x, screen_adjust_y):
                bullet.draw(screen_adjust_x, screen_adjust_y, screen)
            else:
                self._bullets.remove(bullet)

    def isprint_range(self, bullet: BulletObject, screen_adjust_x: int, screen_adjust_y: int) -> bool:
        isxrange: bool = bullet.rect.left - \
            screen_adjust_x > 0 and bullet.rect.right - screen_adjust_x < self.SCREENWIDTH
        isyrange: bool = bullet.rect.top - screen_adjust_y > 0 and bullet.rect.bottom - \
            screen_adjust_y < self.SCREENHEIGHT
        return isxrange and isyrange

class BulletObject():
    def __init__(self, playerpoint: Rect, isRight: bool, bulletImage: Surface) -> None:
        super().__init__()
        self._vector: int = 1 if isRight else -1
        self._xDiff: int = 20 if isRight else 0 # 発射主からどれだけずれた位置を始点とするかを判別する関数
        self.rect: Rect = Rect(
            playerpoint.x + self._xDiff, playerpoint.y + 8, 8, 6)
        self._busterV: int = 5
        self.bulletImage: Surface = bulletImage
        self._power = 1

    @property
    def vx(self) -> int:
        return self._busterV * self._vector

    @property
    def power(self) -> int:
        return self._power

    def update(self) -> None:
        self.rect.x += self.vx

    def draw(self, screen_adjust_x: int, screen_adjust_y: int, screen: Surface) -> None:
        screen.blit(self.bulletImage, (self.rect.x -
                    screen_adjust_x, self.rect.y - screen_adjust_y))