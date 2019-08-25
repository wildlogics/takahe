#!/usr/bin/python
# -*- coding: utf-8 -*-
import vulkan

from takahe.compositor.types import LogicalDevice
from takahe.render.types import Pipeline


class CommandPool():

    def __init__(self, device, vk_command_pool):

        self.device = device
        self.vk_command_pool = vk_command_pool

    def create_buffers(self, amount):

        allocate = vulkan.VkCommandBufferAllocateInfo(
            commandPool = self.vk_command_pool,
            level = vulkan.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount = amount
        )

        self.vk_command_buffers = vulkan.vkAllocateCommandBuffers(self.device.vk_device, allocate)
        buffers = [CommandBuffer(self.vk_command_buffers[idx]) for idx in range(len(self.vk_command_buffers))]
        return buffers

    def destroy(self):

        vulkan.vkFreeCommandBuffers(self.device.vk_device, self.vk_command_pool, len(self.vk_command_buffers), self.vk_command_buffers)
        vulkan.vkDestroyCommandPool(self.device.vk_device, self.vk_command_pool, None)


class CommandBuffer():

    def __init__(self, vk_command_buffer):

        self.vk_command_buffer = vk_command_buffer

    def begin(self):

        begin = vulkan.VkCommandBufferBeginInfo(
            flags = vulkan.VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT,
            pInheritanceInfo = None
        )

        vulkan.vkBeginCommandBuffer(self.vk_command_buffer, begin)

    def bind(self, pipeline : Pipeline):

        vulkan.vkCmdBindPipeline(self.vk_command_buffer, vulkan.VK_PIPELINE_BIND_POINT_GRAPHICS, pipeline.vk_pipelines[0])

    def draw(self):

        vulkan.vkCmdDraw(self.vk_command_buffer, 3, 1, 0 ,0)

    def end(self):

        vulkan.vkEndCommandBuffer(self.vk_command_buffer)


