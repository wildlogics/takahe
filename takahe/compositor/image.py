#!/usr/bin/python
# -*- coding: utf-8 -*-
import vulkan

from takahe.base.types import PhysicalDevice


class ImageView():

    def __init__(self, device : PhysicalDevice, vk_imageview):

        self.device = device
        self.vk_imageview = vk_imageview

    def destroy(self):

        vulkan.vkDestroyImageView(self.device.vk_device, self.vk_imageview, None)