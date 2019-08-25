#!/usr/bin/python
# -*- coding: utf-8 -*-
import vulkan

from takahe.compositor.types import LogicalDevice


class VulkanSemaphore():

    def __init__(self, device : LogicalDevice):

        self.device = device
        self.init()

    def init(self):

        create = vulkan.VkSemaphoreCreateInfo()
        self.vk_semaphore = vulkan.vkCreateSemaphore(self.device.vk_device, create, None)

    def destroy(self):

        vulkan.vkDestroySemaphore(self.device.vk_device, self.vk_semaphore, None)



