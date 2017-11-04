#coding=utf-8
"""
Tarea 2.E - Kingdoms Warfare (Bacto)
Debes conquistar los casitllos del mapa, generar poblacion y eliminar al enemigo.
"""

import pygame
import os
import ai_enemigo

from pygame.locals import *

from dibujos import *
from utilitarios import *
from constants import *


#Fundamentales
pygame.init()
os.environ['SLD_VIDEO_CENTERED'] = '1'
clock=pygame.time.Clock()
screen = pygame.display.set_mode((ANCHO,ALTO))

#Dibujo borde superior ventana
icono = pygame.image.load('images/icon.PNG')
pygame.display.set_caption('Kingdoms Warfare')                          #Titulo Ventana
pygame.display.set_icon(icono)                                          #Icono Ventana

#Dibujo menu inicio
draw_menu(screen)


#Estados
ESTADO = 'MENU'         #Estado programa
pausa = False           #Estado partida

#Elementos destacados (highlighted)
hl_select=''                            #Parametro destacar boton en menu seleccion
hl_castillo = None                      #Castillo 1 destacado en partida
castillo_seleccionado = None            #Castillo seleccionado para ataque

#Variables programa
tiempo=0
tiempo_mil=0
linea=0

#Musica
pygame.mixer.music.load('music/background.mp3')
pygame.mixer.music.play(-1)
gate = pygame.mixer.Sound('sounds/gate.wav')

while True:

    #Se setea el reloj
    clock.tick(60)
    frame_mil = clock.get_time()
    ev=pygame.event.get()
    cursor = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    for event in ev:
        if event.type == QUIT:
            exit()

    #Estado menu principal
    if ESTADO=='MENU':
        if cursor_en(cursor,C_START):
            draw_menu(screen, 'start')
            for event in ev:
                if event.type == pygame.MOUSEBUTTONUP:
                    gate.play()
                    print 'Estado: Seleccion'
                    ESTADO='SELECCION'
                    draw_select(screen)
                    continue
        else:
            draw_menu(screen)




    #Estado menu seleccion
    elif ESTADO=='SELECCION':
            #Coordenadas inconos reinos
        for coo_kd in COO_SELEC_KINGDOMS:
            if cursor_en(cursor,coo_kd):
                index_castillo = COO_SELEC_KINGDOMS.index(coo_kd)
                hl_select=str(index_castillo)
                for event in ev:
                    #Si se presiona un icono de un reino
                    if event.type == pygame.MOUSEBUTTONUP:
                        gate.play()

                        #Se escoge el reino enemigo
                        index_enemigo=index_castillo
                        while index_enemigo==index_castillo:
                            index_enemigo=rn.randint(0,5)

                        #Asignacion de reino a los jugadores
                        Player = Kingdoms[index_castillo]
                        Pc = Kingdoms[index_enemigo]

                        #Generacion de castillos del mapa
                        print 'generando castillos.'
                        castillos = gen_castillos(Player,Pc)
                        print 'castillos generados.'
                        soldados=[]

                        #Reinicio temporisador
                        tiempo = 0
                        tiempo_mil = 0

                        #Dibujo pantalla partida
                        draw_gamescreen(screen, castillos, soldados, tiempo, hl_castillo, castillo_seleccionado, linea, pausa)
                        ESTADO = 'JUEGO'
                        print "Estado: Juego"
                        continue
        if ESTADO=='JUEGO':
            continue

        #Boton volver a menu inicial
        if cursor_en(cursor,C_SELEC_MENU):
            hl_select='menu'
            for event in ev:
                if event.type == pygame.MOUSEBUTTONUP:
                    gate.play()
                    print "Estado: menu"
                    ESTADO = 'MENU'
                    draw_menu(screen)
                    continue
        draw_select(screen, hl_select)
        hl_select=''




    #Estado partida juego
    elif ESTADO=='JUEGO':
        for event in ev:
            if event.type == pygame.KEYUP:

                if event.key == pygame.K_m:
                    print "Estado: menu"
                    ESTADO = 'MENU'
                    draw_menu(screen)
                    continue

                if event.key == pygame.K_ESCAPE:
                    pausa = not pausa
                    print 'pausa', pausa

        if ESTADO == 'MENU':
            continue

        if not pausa:
            #Iteracion sobre castillos

            ai_enemigo.ia_enemigo(Pc, castillos, soldados, 'NORMAL')

            est_player = False
            est_pc = False

            for c in castillos:
                c.crecer_poblacion(float(frame_mil)/1000)
                #Deteccion mouse sobre castillo
                if c.choque_cursor(cursor):

                    #Castillo bajo el mouse
                    hl_castillo=c

                    #Seleccion de castillos para envio de caravana
                    if click[0]:
                        if castillo_seleccionado is None and c.ocupante == Player:
                            castillo_seleccionado = c

                    else:
                        if c != castillo_seleccionado and castillo_seleccionado is not None:
                            castillo_seleccionado.invadir(c,soldados)
                            print 'Envio soldados'
                            castillo_seleccionado = None


                if c.ocupante == Player:
                        est_player = True

                if c.ocupante == Pc:
                        est_pc = True



            #Iteracion sobre soldados
            for s in soldados:
                mov_s=s.mover(float(frame_mil)/1000, castillos)
                if mov_s==-1 or not cursor_en(s.posicion, [0, 0, ANCHO, ALTO]):
                    soldados.remove(s)


            #Parte de selecion de castillos para envio de caravana (deseleccion de castillo)
            if not click[0]:
                    castillo_seleccionado=None

            #Tiempo partida (segundos)
            tiempo_mil=tiempo_mil+frame_mil
            if tiempo_mil>=1000:
                tiempo_mil=tiempo_mil-1000
                tiempo=tiempo+1

            if castillo_seleccionado is not None:
                pt1=castillo_seleccionado.centro
                pt2=cursor
                if hl_castillo is not None:
                    pt2 = hl_castillo.centro
                linea= [pt1, pt2]

            else:
                linea=0

        if not est_player or  not est_pc:
            print 'Estado: game over'
            ESTADO = 'GAME_OVER'
            continue


        draw_gamescreen(screen, castillos, soldados, tiempo, hl_castillo, castillo_seleccionado, linea, pausa)
        hl_castillo=None

    elif ESTADO == 'GAME_OVER':
        ganador = 'victoria!'
        if not est_player:
            ganador = 'derrota'
        draw_game_over(screen, castillos, soldados, tiempo, ganador)
        for event in ev:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_m:
                    print "Estado: menu"
                    ESTADO = 'MENU'
                    draw_menu(screen)
                    continue

        ############################