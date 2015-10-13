# -*- coding:utf-8 -*-
import numpy as np
from numpy.fft import fft2, ifft2, fftshift
from pprint import pprint
from PIL import Image
import pickle
from math import *

texture_path = 'texture/'
config_path = 'config/'

replaceList = {'SimpleScreen': '简单接收屏', 'SimpleFreeSpace': '简单自由空间传播', 'dist': '距离(mm)', 'WaveFront': '波面', 'amp': '振幅', 'lam': '波长(nm)', 'span': '尺寸(默认)(mm)', 'reso': '分辨率(默认)', 'WaveFrontGroup': '波组', 'PlaneWave': '平面波', 'angle': '传播方向([x, y, z])(mm)', 'SphereWave': '球面波', 'pos': '位置([x, y, z])(mm)', 'inOrOut': '发散(1)/收缩(-1)', 'WaveFliter': '滤波器', 'Len': '透镜', 'f': '焦距(mm)', 'ExpressFliter': '任意表达式滤波器', 'express': '表达式', 'Aperture': '光阑', 'SquareAperture': '矩形光阑', 'xspan': '孔水平长度(mm)', 'yspan': '孔竖直长度(mm)', 'center': '中心([u, v])', 'CircleAperture': '圆形光阑', 'r': '半径(mm)', 'reverse': '中心透光(0)/周围透光(1)', 'MultiSplitAperture': '多缝', 'a': '缝宽(mm)', 'd': '缝间距(mm)', 'num': '缝数', 'FresnelPlateAperture': '菲涅尔波带片', 'evenOrOdd': '偶数片(0)/奇数片(1)', 'roundOrSquare': '圆形(1)/方形(0)', 'ImageAperture': '图像光阑', 'imgPath': '路径', 'Screen': '接收屏', 'thr': '阈值', 'FreeSpace': '自由空间传播', 'z': '传播距离(mm)', 'useLog': '线性显示(0)/对数显示(1)'}

class Element:
    def __init__(self):
        default = self.getSpanAndReso()
        self.span = default['span']
        self.reso = default['reso']
        #self.fftFactor = self.reso**2 / 2
        self.fftFactor = 1
    def getSpanAndReso(self):
        with open(config_path + r'cfg.txt', 'rb') as f:
            temp = pickle.load(f)
        return temp

class WaveFront(Element):
    def __init__(self, amp, lam):
        super().__init__()
        self.amp = amp
        self.lam = lam * 1e-6
        self.k = 2 * np.pi / self.lam
        self.x, self.y = np.mgrid[-self.span: self.span: self.reso*1j, -self.span: self.span: self.reso*1j]
        self.thr = 0
    def toDict(self):
        return {'amp': self.amp, 'lam': self.lam * 1e6} 
    def transport(self, freeSpace):
        z = freeSpace.z
        zc = self.reso * (2*self.span/self.reso)**2 / self.lam
        #if np.all(self.waveFront == np.ones_like(self.waveFront) * self.waveFront[0, 0]):
        #    return self
        #'''
        if z > zc:
            freqDomient = fft2(self.waveFront)
            h = np.exp(1j*self.k*z) / (1j*self.lam*z) * np.exp(1j*(self.x**2+self.y**2)*self.k/(2*z))
            H = fft2(h)
            freqDomient *= H
            self.waveFront = fftshift(ifft2(freqDomient)) / self.fftFactor
        else:
            freqDomient = fft2(self.waveFront)
            maxFreq = self.reso / (self.span * 4)
            fx, fy = np.mgrid[-maxFreq: maxFreq: self.reso * 1j, -maxFreq: maxFreq: self.reso * 1j]
            H = np.exp(1j * self.k * z * np.sqrt(1 + 0j - (self.lam * fx)**2 - (self.lam * fy)**2))
            freqDomient *= fftshift(H)
            self.waveFront = ifft2(freqDomient) / self.fftFactor
        return self
    def waveFrontChange(self, waveFliter):
        self.waveFront *= waveFliter.fliter(self.k)
        return self
    def throughAperture(self, aperture):
        self.waveFront *= aperture.stop
        return self
    def I(self):
        return np.abs(self.waveFront)**2
    def __mul__(self, other):
        if isinstance(other, WaveFliter):
            return self.waveFrontChange(other)
        elif isinstance(other, Aperture):
            return self.throughAperture(other)
        elif isinstance(other, Screen):
            other.I = self.I()
            self.thr = other.thr
            return self
        elif isinstance(other, FreeSpace):
            return self.transport(other)
        else:
            raise TypeError('Wrong type')
    def __add__(self, other):
        if isinstance(other, WaveFront):
            if self.lam == other.lam:
                w = WaveFront(self.amp, self.lam)
                w.waveFront = self.waveFront + other.waveFront
                return w
            else:
                wg = WaveFrontGroup()
                wg.add(self)
                wg.add(other)
                return wg
        elif isinstance(other, WaveFrontGroup):
            return other + self
        else:
            raise TypeError('Wrong type')
    def show(self, i):
        I = self.I()
        if self.thr:
            I[I > self.thr] = self.thr
        print(np.max(I))
        im =  Image.fromarray(I / np.max(I) * 255)
        im =  im.convert('RGB')
        im.save(texture_path + str(i) + r'.png', 'PNG')

class WaveFrontGroup:
    def __init__(self):
        self.waveGroup = []
    def toDict(self):
        return [i.toDict() for i in self.waveGroup]
    def add(self, w):
        self.waveGroup.append(w)
    def I(self):
        I = 0
        for w in self.waveGroup:
            I += w.I()
        return I
    def __mul__(self, other):
        if isinstance(other, WaveFliter):
            for w in self.waveGroup:
                w.waveFrontChange(other)
            return self
        elif isinstance(other, Aperture):
            for w in self.waveGroup:
                w.throughAperture(other)
            return self
        elif isinstance(other, Screen):
            other.I = self.Ig()
            return self.show(other.thr)
        elif isinstance(other, FreeSpace):
            for w in self.waveGroup:
                w.transport(other)
            return self
        else:
            raise TypeError('Wrong type')
    def __add__(self, other):
        if isinstance(other, WaveFront):
            wg = WaveFrontGroup()
            flag = False
            for w in self.waveGroup:
                if w.lam == other.lam:
                    w.waveFront += other.waveFront
                    wg.add(w)
                else:
                    wg.add(w)
            if flag == False:
                wg.add(other)
            return wg
        else:
            raise TypeError('Wrong type')
    def Ig(self):
        Ig = 0
        for w in self.waveGroup:
            I = w.I()
            Ig += I
        return Ig
    def show(self, i, thr = 0):
        Ig = self.Ig()
        if thr:
            Ig[Ig > self.thr] = self.thr
        im =  Image.fromarray(Ig)
        im =  im.convert('RGB')
        im.save(texture_path + str(i) + r'.png', 'PNG')

class PlaneWave(WaveFront):
    def __init__(self, amp, lam, angle):
        super().__init__(amp, lam)
        self.angle = angle / np.sqrt(sum([i**2 for i in angle]))
        self.waveFront = np.exp(1j * self.k * (self.angle[0]*self.x + self.angle[1]*self.y))
    def toDict(self):
        t = super().toDict()
        t['angle'] = self.angle.tolist()
        return t

class SphereWave(WaveFront):
    def __init__(self, amp, lam, pos, inOrOut = 1):
        super().__init__(amp, lam)
        self.inOrOut = inOrOut
        self.pos = pos
        self.u, self.v, self.w = self.pos
        self.waveFront = np.exp(self.inOrOut*1j*self.k*np.sqrt((self.x-self.u)**2 + (self.y-self.v)**2 + self.w**2))
    def toDict(self):
        t = super().toDict()
        t['inOrOut'] = self.inOrOut
        t['pos'] = self.pos
        return t

class WaveFliter(Element):
    def __init__(self):
        super().__init__()
        self.x, self.y = np.mgrid[-self.span: self.span: self.reso*1j, -self.span: self.span: self.reso*1j]
    def toDict(self):
        return {}
    def fliter(self, k):
        return np.exp(1j * k * self.opd)
    def show(self, i):
        im =  Image.fromarray(np.abs(self.opd) / np.max(np.abs(self.opd)) * 255)
        im =  im.convert('RGB')
        im.save(texture_path + str(i) + r'.png', 'PNG')
    def __mul__(self, other):
        pass

class Len(WaveFliter):
    def __init__(self, f):
        super().__init__()
        self.f = f
        #self.opd = -(np.sqrt(self.x**2 + self.y**2 + self.f**2) - self.f)
        self.opd = -(self.x**2+self.y**2) / (2*self.f)
    def toDict(self):
        t = super().toDict()
        t['f'] = self.f
        return t

class ExpressFliter(WaveFliter):
    def __init__(self, express):
        super().__init__()
        self.express = express
        self.func = np.vectorize(eval('lambda x, y:' + express))
        self.opd = self.func(self.x, self.y)
    def toDict(self):
        t = super().toDict()
        t['express'] = self.express
        return t

class Aperture(Element):
    def __init__(self):
        super().__init__()
        self.x, self.y = np.mgrid[-self.span: self.span: self.reso*1j, -self.span: self.span: self.reso*1j]
        self.gray = 150
    def toDict(self):
        return {}
    def show(self, i):
        bg = np.uint8(np.ones((self.reso, self.reso, 4)) * self.gray)
        bg[:, :, 3] = np.uint8(255 - self.stop * 255)
        im =  Image.fromarray(bg)
        im =  im.convert('RGBA')
        im.save(texture_path + str(i) + r'.png', 'PNG')
    def __add__(self, other):
        if isinstance(other, Aperture):
            a = Aperture()
            a.stop = self.stop + other.stop
            return a
        else:
            raise TypeError('Wrong type')
    def __mul__(self, other):
        pass

class SquareAperture(Aperture):
    def __init__(self, xspan, yspan, center):
        super().__init__()
        self.xspan = xspan
        self.yspan = yspan
        self.center = center
        self.u, self.v = self.center
        self.stop = np.logical_and(np.abs(self.x-self.u) < xspan, np.abs(self.y-self.v) < yspan)
    def toDict(self):
        t = super().toDict()
        t['xspan'] = self.xspan
        t['yspan'] = self.yspan
        t['center'] = self.center
        return t

class CircleAperture(Aperture):
    def __init__(self, r, center, reverse = 0):
        super().__init__()
        self.center = center
        self.u, self.v = self.center
        self.r = r
        self.reverse = reverse
        if not reverse:
            self.stop = ((self.x-self.u)**2 + (self.y-self.v)**2) < r**2
        else:
            self.stop = ((self.x-self.u)**2 + (self.y-self.v)**2) > r**2
    def toDict(self):
        t = super().toDict()
        t['r'] = self.r
        t['center'] = self.center
        t['reverse'] = self.reverse
        return t


class MultiSplitAperture(Aperture):
    def __init__(self, a, d, num):
        super().__init__()
        self.a = a
        self.d = d
        self.num = num
        self.stop = np.zeros_like(self.x)
        y = self.y[0]
        for i in range(num - 1):
            index = np.logical_and(np.abs(y) > ((0.5+i)*d - a/2), np.abs(y) < ((0.5+i)*d + a/2))
            self.stop[self.reso//2, index] = 1
    def toDict(self):
        t = super().toDict()
        t['a'] = self.a
        t['d'] = self.d
        t['num'] = self.num
        return t
    def show(self, i):
        #self.stop
        stop = np.zeros_like(self.x)
        for idx in range(self.num - 1):
            index = np.logical_and(np.abs(self.y) > ((0.5+idx)*self.d - self.a/2), np.abs(self.y) < ((0.5+idx)*self.d + self.a/2))
            stop[index] = 1
        bg = np.uint8(np.ones((self.reso, self.reso, 4)) * self.gray)
        bg[:, :, 3] = np.uint8(255 - stop * 255)
        im = Image.fromarray(bg)
        im = im.convert('RGBA')
        im.save(texture_path + str(i) + r'.png', 'PNG')

class FresnelPlateAperture(Aperture):
    def __init__(self, dist, lam, r, evenOrOdd, roundOrSquare):
        super().__init__()
        lam = lam * 1e-6
        self.dist = dist
        self.r = r
        self.lam = lam
        self.evenOrOdd = evenOrOdd
        self.roundOrSquare = roundOrSquare
        n = int(2 * (np.sqrt(dist**2 + r**2) - dist) / lam) + 1
        if roundOrSquare:
            foo = lambda x, y: np.sqrt(x**2 + y**2)
        else:
            foo = lambda x, y: abs(x) if abs(x) > abs(y) else abs(y)
        foo = np.vectorize(foo)
        d = foo(self.x, self.y)
        self.stop = np.zeros_like(self.x)
        self.stop[d < r] = 1
        for i in range(evenOrOdd, n, 2):
            r1 = np.sqrt((dist + i*lam/2)**2 - dist**2)
            r2 = np.sqrt((dist + (i+1)*lam/2)**2 - dist**2)
            index = np.logical_and(d > r1 , d < r2)
            self.stop[index] = 0
    def toDict(self):
        t = super().toDict()
        t['dist'] = self.dist
        t['r'] = self.r
        t['lam'] = self.lam
        t['evenOrOdd'] = self.evenOrOdd
        t['roundOrSquare'] = self.roundOrSquare
        return t

class ImageAperture(Aperture):
    def __init__(self, imgPath):
        super().__init__()
        self.imgPath = imgPath
        img = np.asarray(Image.open(self.imgPath), dtype = np.uint8).T
        self.stop = img.copy() / 255
    def toDict(self):
        t = super().toDict()
        t['imgPath'] = self.imgPath
        return t

class Screen(Element):
    def __init__(self, thr = 0, useLog = 0):
        super().__init__()
        self.thr = thr
        self.useLog = useLog
        self.I = np.zeros((self.reso, self.reso))
    def toDict(self):
        return {'thr': self.thr, 'useLog': self.useLog}
    def show(self, i):
        if self.thr != 0:
            self.I[self.I > self.thr] = self.thr
        if self.useLog != 0:
            self.I = np.log(self.I + 1)
        im =  Image.fromarray(self.I / np.max(self.I) * 255)
        im =  im.convert('RGB')
        im.save(texture_path + str(i) + r'.png', 'PNG')
    def __mul__(self, other):
        pass
        
class SimpleScreen(Screen):
    def __init__(self, thr = 0, useLog = 0):
        super().__init__(thr, useLog)

class FreeSpace:
    def __init__(self, z):
        self.z = z
    def toDict(self):
        return {'z': self.z}
    def show(self, i):
        pass

class SimpleFreeSpace(FreeSpace):
    def __init__(self, z):
        super().__init__(z)

class Data:
    pass

baseClassType = ['Aperture', 'WaveFront', 'WaveFliter', 'FreeSpace', 'Screen', 'WaveFrontGroup']
classInherit = {}
classInheritForJS = {}
for b in baseClassType:
    classInherit[b] = {'arg':[], 'paras':{}, 'subclasses':{}}
    classInheritForJS[b] = {'paras':{}, 'subclasses':{}}

importList = dir()
for c in importList:
    if type(eval(c)).__name__ == 'type' and eval(c).__name__ in baseClassType:
        argList = list(reversed(eval(c).__init__.__code__.co_varnames[1:eval(c).__init__.__code__.co_argcount]))
        classInherit[eval(c).__name__]['arg'] = argList
        defaultArg = []
        if eval(c).__init__.__defaults__:
            defaultArg = list(reversed(eval(c).__init__.__defaults__))
        for (i, arg) in enumerate(argList):
            classInherit[eval(c).__name__]['paras'][arg] = Data()
            if i < len(defaultArg):
                classInherit[eval(c).__name__]['paras'][arg].para = defaultArg[i]
                classInheritForJS[eval(c).__name__]['paras'][arg] = defaultArg[i]
            else:
                classInherit[eval(c).__name__]['paras'][arg].para = 0
                classInheritForJS[eval(c).__name__]['paras'][arg] = 0
    elif type(eval(c)).__name__ == 'type' and eval(c).__bases__[0].__name__ in baseClassType:
        classInherit[eval(c).__bases__[0].__name__]['subclasses'][eval(c).__name__] = {}
        classInheritForJS[eval(c).__bases__[0].__name__]['subclasses'][eval(c).__name__] = {}
        argList = list(reversed(eval(c).__init__.__code__.co_varnames[1:eval(c).__init__.__code__.co_argcount]))
        classInherit[eval(c).__bases__[0].__name__]['subclasses'][eval(c).__name__]['arg'] = argList
        defaultArg = []
        if eval(c).__init__.__defaults__:
            defaultArg = list(reversed(eval(c).__init__.__defaults__))
        for (i, arg) in enumerate(argList):
            classInherit[eval(c).__bases__[0].__name__]['subclasses'][eval(c).__name__][arg] = Data()
            if i < len(defaultArg):
                classInherit[eval(c).__bases__[0].__name__]['subclasses'][eval(c).__name__][arg].para = defaultArg[i]
                classInheritForJS[eval(c).__bases__[0].__name__]['subclasses'][eval(c).__name__][arg] = defaultArg[i]
            else:
                classInherit[eval(c).__bases__[0].__name__]['subclasses'][eval(c).__name__][arg].para = 0
                classInheritForJS[eval(c).__bases__[0].__name__]['subclasses'][eval(c).__name__][arg] = 0

