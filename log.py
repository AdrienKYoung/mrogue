#part of mrogue, an interactive adventure game
#Copyright (C) 2017 Adrien Young and Tyler Soberanis
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import consts

_logger = open("log.txt","w")

def info(module,message,values):
    if module in consts.DEBUG_DETAIL_LOGGING:
        _logger.write("[INFO][{}] ".format(module) + message.format(*values) + "\n")

def warn(module,message,values):
    if module in consts.DEBUG_DETAIL_LOGGING:
        _logger.write("[WARN][{}] ".format(module) + message.format(*values) + '\n')

def error(module,message,values):
    _logger.write("[ERROR][{}] ".format(module) + message.format(*values) + '\n')
