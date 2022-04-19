#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 15:47:36 2022

@author: gabi
"""

import pygame as pg
from pygame import midi
import random as rnd
import sys
import time

x,y=8,6
size=64
width=x*size
height=y*size
fps=30
white=255,255,255


pg.init()



pg.mixer.init()
screen=pg.display.set_mode((width,height))
pg.display.set_caption("Midi-Rush")
clock=pg.time.Clock()

face = pg.image.load("./game-data/"+str(size)+"/player.gif")
facerect = face.get_rect(center=(size*4,size*3))
speed =[3,5]
rollspeed=5
d=0.01 # Dämpfungsfaktor



class map:
    def __init__(self,karte="./game-data/karte.txt"):
        '''
        geladen wird karte.txt mit den Buchstaben b,g,f,t
        Struktur self.karte={(Zeile,Spalte):[Sprite,Sprite_rect,Buchstabe]}

        '''
        self.karte={}
        self.wall=set()
        self.side=set()
        self.sprites={}
        self.speed=[0,0]
        text=open(karte,'r')
        lines=text.readlines()
        c_line=0
        for line in lines:
            c_char=0
            for char in line:
                c=(c_line,c_char)
                print(char,c)
                if char=='b':
                    self.karte[c]=[pg.image.load("./game-data/"+str(size)+"/blue.gif"),None,char]
                    self.addrect(c)
                elif char=='g':
                    self.karte[c]=[pg.image.load("./game-data/"+str(size)+"/gras.gif"),None,char]
                    self.addrect(c)
                elif char=='f':
                    self.karte[c]=[pg.image.load("./game-data/"+str(size)+"/green.gif"),None,char]
                    self.addrect(c)
                    self.wall.add((c[1],c[0]))
                elif char=='t':
                    self.karte[c]=[pg.image.load("./game-data/"+str(size)+"/brown.gif"),None,char]
                    self.addrect(c)
                    self.wall.add((c[1],c[0]))
                    
                #print(self.karte[c][1])
                #self.karte[c][1].x=
                #self.karte[c][1].y=64*c[0]
                #print(self.karte[c][1])
                c_char+=1
            c_line+=1
            print(c)
        text.close()
        for w in self.wall:
            #links frei
            if (w[0]-1,w[1]) not in self.wall: 
                self.side.add((0,w))
            #rechts frei
            if (w[0]+1,w[1]) not in self.wall:
                self.side.add((1,w))
            #links und rechts frei
            if (0,w) in self.side and (1,w) in self.side:
                #self.side.remove((0,w))
                #self.side.remove((1,w))
                self.side.add((2,w))
            #braune Deckengarnitur
            if (w[0],w[1]+1) not in self.wall and self.karte[(w[1],w[0])][2]=='t':
                print(w,self.karte[(w[1],w[0])])
                self.sprites[(w[1]+1,w[0])]=[pg.image.load("./game-data/"+str(size)+"/stalag.gif"),None,char]
                self.addrect((w[1]+1,w[0]),'sprite')
            #grünes gras
            if (w[0],w[1]-1) not in self.wall and self.karte[(w[1],w[0])][2]=='f':
                print(w,self.karte[(w[1],w[0])])
                self.sprites[(w[1]-1,w[0])]=[pg.image.load("./game-data/"+str(size)+"/grass.gif"),None,char]
                self.addrect((w[1]-1,w[0]),'sprite')
        
        self.wall0=self.wall.copy()
        self.side0=self.side.copy()
    def addrect(self,c,typ='karte'):
        if typ!='karte':
            self.sprites[c][1]=self.sprites[c][0].get_rect(topleft=(size*c[1],size*c[0]))
        else:    
            self.karte[c][1]=self.karte[c][0].get_rect(topleft=(size*c[1],size*c[0]))
    def read(self,coord):
        return self.karte(coord)
    def mov(self,speed):
        for sprite in self.karte:
            self.karte[sprite][1]=self.karte[sprite][1].move(speed)
        for sprite in self.sprites:
            self.sprites[sprite][1]=self.sprites[sprite][1].move(speed)
        stack=set()
        for pos in self.wall0:
            stack.add((int(self.karte[(pos[1],pos[0])][1].midtop[0]/size),int(self.karte[(pos[1],pos[0])][1].midtop[1]/size)))
            self.wall=stack.copy()
        stack=set()
        for pos in self.side0:
            stack.add((pos[0],(int(self.karte[(pos[1][1],pos[1][0])][1].midtop[0]/size),int(self.karte[(pos[1][1],pos[1][0])][1].midtop[1]/size))))
        self.side=stack.copy()
    
m=map()

print()
   
class player:
    def __init__(self,img="./game-data/"+str(size)+"/player.gif"):
        self.fig=pg.image.load(img)
        self.figrect=self.fig.get_rect(topleft=(size*1,size*3))
        self.speed=[0,3]
        self.angle=0
        self.anglespeed=-2
        #positionen
        #rechts unten
        self.br=(int(self.figrect.bottomright[0]/size),int(self.figrect.bottomright[1]/size))
        #links unten
        self.bl=(int(self.figrect.bottomleft[0]/size),int(self.figrect.bottomleft[1]/size))
        #rechts oben
        self.tr=(int(self.figrect.topright[0]/size),int(self.figrect.topright[1]/size))
        #link soben
        self.tl=(int(self.figrect.topleft[0]/size),int(self.figrect.topleft[1]/size))
        
        
    def update(self):
        #positionen
        #rechts unten
        self.br=(int(self.figrect.bottomright[0]/size),int(self.figrect.bottomright[1]/size))
        #links unten
        self.bl=(int(self.figrect.bottomleft[0]/size),int(self.figrect.bottomleft[1]/size))
        #rechts oben
        self.tr=(int(self.figrect.topright[0]/size),int(self.figrect.topright[1]/size))
        #link soben
        self.tl=(int(self.figrect.topleft[0]/size),int(self.figrect.topleft[1]/size))
        #mitte unten
        self.mb=(int(self.figrect.midbottom[0]/size),int(self.figrect.midbottom[1]/size))
        #mitte oben
        self.mt=(int(self.figrect.midtop[0]/size),int(self.figrect.midtop[1]/size))
        #Gravitation
    def grav(self):    
        self.speed[1]+=10/fps*size/64#-self.speed[1]*d
        #if self.speed[1]>0:
        #    self.speed[1]+=10/fps-self.speed[1]**2*d
        #elif self.speed[1]<0:p.rotate()
        #    self.speed[1]+=10/fps+self.speed[1]**2*d
    def fric(self):
        self.speed[0]=self.speed[0]*0.25*size/64
    def rotate(self):
        self.angle=(self.angle+self.anglespeed)%360
        copy=self.figrect.copy()
        self.fig=pg.transform.rotate(self.fig, self.anglespeed)
        center=self.figrect.center
        self.figrect=copy
        self.figrect=self.fig.get_rect(center=center)
        
        
def pos(coord,shift_y=0):
    if shift_y!=0:
        return (int(coord[0]/size),(int((coord[1]-shift_y)/size)))
    return (int(coord[0]/size),int(coord[1]/size))


class button:
    def __init__(self, text, pos):
        self.pos=pos
        self.font = pg.font.SysFont("Arial", int(size/8))
        self.button=self.font.render(text,True,pg.Color('White'))
        self.size=self.button.get_size()
        self.surface=pg.Surface(self.size)
        self.surface.blit(self.button,(0,0))
    def draw(self):
        screen.blit(self.surface, self.pos)
 
p=player()
print(m.sprites)
rotate=False


#midi

midi.init()

#default_id = 5 #midi.get_default_input_id()
#midi_input = midi.Input(device_id=default_id)
midimenu = True



def mid_menu():
    for i in range(midi.get_count()):
        print('release')
        time.sleep(2)
        try:
            midi_input=midi.Input(device_id=i)
            print('Press a key on the midi device.')
            time.sleep(2)
            if midi_input.poll():
                print('device id=',i,' (success)')
                return True, i
        except:
            print('You or the device failed!')
        print(i)
        midi.quit()
        midi.init()
    return None

startbutton=button('Starte das verdammte Spiel Du Hurensohn',(0,0))

running=True
while running:
    
    # Midi-Einrichtung
    
    if midimenu:
        aa,bb=mid_menu()
        if aa==True:
            print(bb)
            midi.quit()
            midi.init()
            midi_input=midi.Input(device_id=bb)
            midimenu=False
        print('Bassdrum, dont press')
        standard_event=[]
        time.sleep(10)
        while len(standard_event)==0:
            for event in midi_input.read(16):
                standard_event.append(event[0])
        print('now press Bass')
        while aa:
            if midi_input.poll():
                for k in midi_input.read(16):
                    if k[0] not in standard_event:
                        print(k,standard_event)
                        bass=k[0]
                        aa=False
                        time.sleep(5)
    # Tastatur-Eingabe
        
    for event in pg.event.get():
        if event.type == pg.QUIT:
            print("STRIKE!!!!!!!!!!!!!!!!!! or p.tl in m.wall or p.tr in m.wall or p.tl in m.wall or p.tr in m.wall!!!!!")
            running= False
            print("hä")
            pg.quit()
            sys.exit()
            
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                
                p.speed[0]=2*size/64
                #
                
                #rotate=True
            if event.key == pg.K_LEFT:
                p.speed[0]=-2*size/64
            if event.key == pg.K_UP and abs(p.speed[1])<3 and (pos(p.figrect.center)[0],pos(p.figrect.center)[1]+1) in m.wall:
                p.speed[1]=-7.5*size/64
        if event.type == pg.KEYUP:
            if event.key == pg.K_RIGHT:
                p.speed[0]-=0.01*size/64
                
                #rotate=False
            if event.key == pg.K_LEFT:
                p.speed[0]+=0.01*size/64

    # Midi-Input
    
    if midi_input.poll():
        for i in midi_input.read(num_events=16):
            if i[0][1]==bass[1]:
                print('BASS')
            
    # Uhr
    
    clock.tick(fps)
    
    # Quatsch
    
    facerect=facerect.move(speed)
    
    #Playerupdate
    
    p.figrect=p.figrect.move(0,p.speed[1])
    m.speed=(-p.speed[0],0)
    m.mov(m.speed)
    p.update() 

    print(p.figrect.midbottom[1]%size,p.mb[1],pos(p.figrect.midbottom,1))    
    if p.mb in m.wall or p.mt in m.wall:
        p.figrect=p.figrect.move((0,-p.speed[1]))
        p.speed[1]=-p.speed[1]*0.35

        #if abs(p.speed[1])<1: or p.tl in m.wall or p.tr in m.wall
        #    p.speed[1]=0#-p.speed[0]*0.35
    if (0,pos(p.figrect.midbottom,1)) in m.side or (0,pos(p.figrect.midtop,-1)) in m.side and p.speed[0]>0:
        print('True')
        p.speed[0]=-3.99*size/64
        m.mov((-p.speed[0],0))
        #p.figrect=p.figrect.move((p.speed[0],0))
        p.fric()
                        #midbottom!!
    if (1,pos(p.figrect.midbottom,1)) in m.side or (1,pos(p.figrect.midtop,-1)) in m.side and p.speed[0]<0:
        print('False')
        p.speed[0]=+3.99*size/64
        m.mov((-p.speed[0],0))
        #p.figrect=p.figrect.move((p.speed[0],0))
        p.fric()
  
        
  
    #gravity + friction
    if p.speed[1]!=0 or (pos(p.figrect.center)[0],pos(p.figrect.center)[1]+1) not in m.wall:
        p.grav()
    if abs(p.speed[0])<2*size/64:
        p.fric()
    #if rotate:
    #    p.rotate()
    
    
    #if p.tl in m.wall and  or p.tr 

    if pos(facerect.center) in m.wall:
        q=0
        for i in range(3):
            if pos(facerect.center) in (i,m.side):
                speed[0]=-speed[0]
                q+=1
                   
        if q==0:
            speed=[-speed[1],-speed[0]]
    
    
    #Darstellung der Karte                

    for k in m.karte:
        screen.blit(m.karte[k][0],m.karte[k][1])
    for k in m.sprites:
        screen.blit(m.sprites[k][0],m.sprites[k][1])
        

    screen.blit(face, facerect)
    s=p.fig.get_rect(center=(p.figrect.center[0]+size/3.5,p.figrect.center[1]))
    screen.blit(p.fig,s)
    startbutton.draw()
    pg.display.flip()
    