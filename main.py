#!/usr/bin/env python

import game_thread

game = game_thread.GameThread(1)
game.start()
game.loop()





