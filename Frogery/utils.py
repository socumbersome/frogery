# -*- coding: utf-8 -*-
import euclid

def vec2point(v):
    return (int(v.x), int(v.y))

def point2vec(p, y = None):
    if y != None:
        return euclid.Vector2(p, y)
    return euclid.Vector2(*p)

