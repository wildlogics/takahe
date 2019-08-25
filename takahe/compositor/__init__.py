#!/usr/bin/python
# -*- coding: utf-8 -*-
from takahe.base.types import BaseEnvironment
from takahe.compositor.ext_swapchain import Swapchain
from takahe.compositor.types import Compositor as Interface

class Compositor(Interface):

    def __init__(self, base : BaseEnvironment):

        self.base = base

    def init(self):

        pysical_device = self.base.vulkan.physical_device
        surface = self.base.vulkan.surface

        self.swapchain = Swapchain(pysical_device, surface)
        self.base.logger.info("Device Surface Capabilities:")
        print(self.swapchain.capabilities())

        layers = self.base.vulkan.vulkan_instance.layers

        device_extensions = []
        device_extensions.extend(self.swapchain.extensions)
        self.device = pysical_device.create_device(surface, layers, device_extensions)

        # self.queue = self.device.get_queue()

        self.swapchain.init(self.device)

    def clean(self):

        self.swapchain.destroy()
        self.device.destroy()