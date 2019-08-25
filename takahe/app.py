#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

from takahe.base import Configuration, BaseEnvironment
from takahe.compositor import Compositor
from takahe.render import Render


class VulkanApplication():

    def __init__(self, configuration : Configuration):

        self.base = BaseEnvironment(configuration)
        self.comp = Compositor(self.base)
        self.draw = Render(self.comp)

    def run(self):

        self.init()
        self.loop()
        self.clean()

    def init(self):

        self.base.init()
        self.comp.init()
        self.draw.init()

    def loop(self):

        self.draw.render()
        self.base.glfw.poll()

    def clean(self):

        self.draw.clean()
        self.comp.clean()
        self.base.clean()

