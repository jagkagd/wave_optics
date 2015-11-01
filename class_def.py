# -*- coding:utf-8 -*-
import numpy as np
from numpy.fft import fft2, ifft2, fftshift
from PIL import Image
import pickle
from math import *
import shutil
from inspect import signature
import json

texture_path = 'texture/'
config_path = 'config/'

replaceList = {'SimpleScreen': '简单接收屏', 'SimpleFreeSpace': '简单自由空间传播', 'dist': '距离(mm)', 'WaveFront': '波面', 'amp': '振幅', 'lam': '波长(nm)', 'span': '尺寸(默认)(mm)', 'reso': '分辨率(默认)', 'WaveFrontGroup': '波组', 'PlaneWave': '平面波', 'angle': '传播方向([x, y, z])(mm)', 'SphereWave': '球面波', 'pos': '位置([x, y, z])(mm)', 'inOrOut': '发散(√)/收缩', 'WaveFliter': '滤波器', 'Len': '透镜', 'f': '焦距(mm)', 'ExpressFliter': '任意表达式滤波器', 'express': '表达式', 'Aperture': '光阑', 'SquareAperture': '矩形光阑', 'xspan': '孔水平长度(mm)', 'yspan': '孔竖直长度(mm)', 'center': '中心([u, v])', 'CircleAperture': '圆形光阑', 'r': '半径(mm)', 'inner': '中心透光(√)/周围透光', 'MultiSplitAperture': '多缝', 'a': '缝宽(mm)', 'd': '缝间距(mm)', 'num': '缝数', 'FresnelPlateAperture': '菲涅尔波带片', 'evenOrOdd': '偶数片(√)/奇数片', 'shape': '形状', 'round': '圆形', 'square': '方形', 'ImageAperture': '图像光阑', 'imgPath': '路径', 'Screen': '接收屏', 'thr': '阈值', 'FreeSpace': '自由空间传播', 'z': '传播距离(mm)', 'useLog': '对数显示(√)/线性显示'}

class Element:
    def __init__(self):
        default = self.getSpanAndReso()
        self.span = default['span']
        self.reso = default['reso']
    def getSpanAndReso(self):
        with open(config_path + r'cfg.txt', 'rb') as f:
            temp = pickle.load(f)
        return temp

class Identity(Element):
    def __init__(self):
        super().__init__()
    def __mul__(self, other):
        return other
    def show(self, i):
        bg = np.uint8(np.zeros((self.reso, self.reso, 4)))
        bg[:, :, 3] = np.uint8(255)
        im =  Image.fromarray(bg)
        im =  im.convert('RGBA')
        im.save(texture_path + str(i) + r'.png', 'PNG')

class WaveFront(Element):
    def __init__(self, amp: float = 1, lam: float = 1000):
        super().__init__()
        self.amp = amp
        self.lam = lam * 1e-6
        self.k = 2 * np.pi / self.lam
        self.x, self.y = np.mgrid[-self.span: self.span: self.reso*1j, -self.span: self.span: self.reso*1j]
        #self.fftFactor = self.reso**2 / 2
        self.milo = 1e3
        self.fftFactor = 1
        self.thr = 0
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
            fx, fy = np.mgrid[-maxFreq: maxFreq: self.reso*1j, -maxFreq: maxFreq: self.reso*1j]
            H = np.exp(1j * self.k * z * np.sqrt(1+0j-(self.lam*fx)**2-(self.lam*fy)**2))
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
            I[I > self.thr*np.max(I)] = self.thr * np.max(I)
        print(np.max(I))
        im =  Image.fromarray(I / np.max(I) * 255)
        im =  im.convert('RGB')
        im.save(texture_path + str(i) + r'.png', 'PNG')

class WaveFrontGroup:
    def __init__(self):
        self.waveGroup = []
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
            Ig[Ig > self.thr*np.max(Ig)] = self.thr * np.max(Ig)
        im =  Image.fromarray(Ig)
        im =  im.convert('RGB')
        im.save(texture_path + str(i) + r'.png', 'PNG')

class PlaneWave(WaveFront):
    def __init__(self, amp: float = 1, lam: float = 1000, angle: [float, float, float] = [0, 0, 1]):
        super().__init__(amp, lam)
        self.angle = angle / np.sqrt(sum([i**2 for i in angle]))
        self.waveFront = np.exp(1j * self.k * (self.angle[0]*self.x + self.angle[1]*self.y))

class SphereWave(WaveFront):
    def __init__(self, amp: float = 1, lam: float = 1000, pos: [float, float, float] = [0, 0, 0], inOrOut: bool = True):
        super().__init__(amp, lam)
        self.inOrOut = inOrOut
        self.pos = pos
        self.u, self.v, self.w = self.pos
        self.waveFront = np.exp(self.inOrOut*1j*self.k*np.sqrt((self.x-self.u)**2 + (self.y-self.v)**2 + self.w**2))

class WaveFliter(Element):
    def __init__(self):
        super().__init__()
        self.x, self.y = np.mgrid[-self.span: self.span: self.reso*1j, -self.span: self.span: self.reso*1j]
    def fliter(self, k):
        return np.exp(1j * k * self.opd)
    def show(self, i):
        im = Image.fromarray(np.abs(self.opd) / np.max(np.abs(self.opd)) * 255)
        im = im.convert('RGB')
        im.save(texture_path + str(i) + r'.png', 'PNG')
    def __mul__(self, other):
        pass

class Len(WaveFliter):
    def __init__(self, f: float = 500):
        super().__init__()
        self.f = f
        self.opd = -(self.x**2+self.y**2) / (2*self.f)
    def show(self, i):
        shutil.copy(r'static/len.png', texture_path + str(i) + r'.png')

class ExpressFliter(WaveFliter):
    def __init__(self, express: str = 'sin(x*y)'):
        super().__init__()
        self.express = express
        self.func = np.vectorize(eval('lambda x, y:' + express))
        self.opd = self.func(self.x, self.y)

class Aperture(Element):
    def __init__(self):
        super().__init__()
        self.x, self.y = np.mgrid[-self.span: self.span: self.reso*1j, -self.span: self.span: self.reso*1j]
        self.gray = 150
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
    def __init__(self, xspan: float = 1, yspan: float = 1, center: [float, float] = [0, 0]):
        super().__init__()
        self.xspan = xspan
        self.yspan = yspan
        self.center = center
        self.u, self.v = self.center
        self.stop = np.logical_and(np.abs(self.x-self.u) < xspan, np.abs(self.y-self.v) < yspan)

class CircleAperture(Aperture):
    def __init__(self, r: float = 1, center: [float, float] = [0, 0], inner: bool = True):
        super().__init__()
        self.center = center
        self.u, self.v = self.center
        self.r = r
        self.inner = inner
        if inner:
            self.stop = ((self.x-self.u)**2 + (self.y-self.v)**2) < r**2
        else:
            self.stop = ((self.x-self.u)**2 + (self.y-self.v)**2) > r**2

class MultiSplitAperture(Aperture):
    def __init__(self, a: float = 0.1, d: float = 1, num: int = 3):
        super().__init__()
        self.a = a
        self.d = d
        self.num = num
        self.stop = np.zeros_like(self.x)
        y = self.y[0]
        for i in range(num - 1):
            index = np.logical_and(np.abs(y) > ((0.5+i)*d - a/2), np.abs(y) < ((0.5+i)*d + a/2))
            self.stop[self.reso//2, index] = 1
    def show(self, i):
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
    def __init__(self, dist: float = 100, lam: float = 1000, r: float = 1, evenOrOdd: bool = True, shape: '|round|square' = 'round'):
        super().__init__()
        lam = lam * 1e-6
        self.dist = dist
        self.r = r
        self.lam = lam
        self.evenOrOdd = evenOrOdd
        self.shape= shape
        n = int(2 * (np.sqrt(dist**2 + r**2)-dist) / lam) + 1
        shapeLambda = {}
        shapeLambda['round'] = lambda x, y: np.sqrt(x**2 + y**2)
        shapeLambda['square'] = lambda x, y: abs(x) if abs(x) > abs(y) else abs(y)
        foo = shapeLambda[shape]
        foo = np.vectorize(foo)
        d = foo(self.x, self.y)
        self.stop = np.zeros_like(self.x)
        self.stop[d < r] = 1
        for i in range(int(evenOrOdd), n, 2):
            r1 = np.sqrt((dist + i*lam/2)**2 - dist**2)
            r2 = np.sqrt((dist + (i+1)*lam/2)**2 - dist**2)
            index = np.logical_and(d > r1 , d < r2)
            self.stop[index] = 0

class ImageAperture(Aperture):
    def __init__(self, imgPath: str = ''):
        super().__init__()
        self.imgPath = imgPath
        img = np.asarray(Image.open(self.imgPath), dtype=np.uint8).T
        self.stop = img.copy() / 255

class Screen(Element):
    def __init__(self, thr: float = 1, useLog: bool = False):
        super().__init__()
        self.thr = thr
        self.useLog = useLog
        self.gray = 150
        self.I = np.ones((self.reso, self.reso)) * self.gray
    def show(self, i):
        if self.thr != 0:
            self.I[self.I > self.thr*np.max(self.I)] = self.thr * np.max(self.I)
        if self.useLog:
            self.I = np.log(self.I + 1)
        im = Image.fromarray(self.I / np.max(self.I) * 255)
        im = im.convert('RGB')
        im.save(texture_path + str(i) + r'.png', 'PNG')
    def __mul__(self, other):
        pass
        
class SimpleScreen(Screen):
    def __init__(self, thr: float = 1, useLog: bool = False):
        super().__init__(thr, useLog)

class FreeSpace(Element):
    def __init__(self, z: float = 0):
        self.z = z
    def show(self, i):
        pass

class SimpleFreeSpace(FreeSpace):
    def __init__(self, z: float = 0):
        super().__init__(z)

class Data:
    pass

def createClassInherit(baseClassName):
    res = { 'args': inspectElementArgs(baseClassName),
            'subClasses': {subClass.__name__: createClassInherit(subClass.__name__) for subClass in eval(baseClassName).__subclasses__() if subClass.__name__ != 'Identity'}}
    return res

def inspectElementArgs(className):
    sig = signature(eval(className).__init__)
    argDict = {}
    for key in sig.parameters:
        if key != 'self':
            argDict[key] = {}
            argDict[key]['annotation'] = transAnnotation(sig.parameters[key].annotation)
            if argDict[key]['annotation'] == 'str' or argDict[key]['annotation'][0] == '|':
                argDict[key]['default'] = sig.parameters[key].default
            else:
                argDict[key]['default'] = json.dumps(sig.parameters[key].default)
    return argDict

def transAnnotation(anno):
    if type(anno).__name__ == 'type':
        res = anno.__name__
    elif type(anno).__name__ == 'list':
        res = []
        for item in anno:
            res.append(transAnnotation(item))
    elif type(anno).__name__ == 'str':
        res = anno
    return res

classInherit = {'Element': createClassInherit('Element')}
classInherit = classInherit['Element']['subClasses']
subClassesInfo = {}
for key, value in classInherit.items():
    for k, v in value['subClasses'].items():
        subClassesInfo[k] = v
