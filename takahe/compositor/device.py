#!/usr/bin/python
# -*- coding: utf-8 -*-
import vulkan

from takahe.commands.types import CommandBuffer
from takahe.compositor.image import ImageView
from takahe.compositor.semaphore import VulkanSemaphore
from .types import LogicalDevice as Interface
from takahe.commands import CommandPool

class LogicalDevice(Interface):

    def __init__(self, logical_device, graphics_family):

        self.vk_device = logical_device
        self.family = graphics_family
        self.graphics_queue = self.get_queue()
        self.present_queue = self.graphics_queue

        from takahe.base.lib_vulkan import DeviceProcAddr
        self.ext = DeviceProcAddr(self.vk_device)

    def get_queue(self):

        queue = vulkan.vkGetDeviceQueue(self.vk_device, self.family.family_id, 0)
        return DeviceQueue(self, queue)

    def create_image_view(self, vk_image, format):

        components = vulkan.VkComponentMapping(
            r=vulkan.VK_COMPONENT_SWIZZLE_IDENTITY,
            g=vulkan.VK_COMPONENT_SWIZZLE_IDENTITY,
            b=vulkan.VK_COMPONENT_SWIZZLE_IDENTITY,
            a=vulkan.VK_COMPONENT_SWIZZLE_IDENTITY
        )

        range = vulkan.VkImageSubresourceRange(
            aspectMask=vulkan.VK_IMAGE_ASPECT_COLOR_BIT,
            baseMipLevel=0,
            levelCount=1,
            baseArrayLayer=0,
            layerCount=1
        )

        create = vulkan.VkImageViewCreateInfo(
            image = vk_image,
            viewType = vulkan.VK_IMAGE_VIEW_TYPE_2D,
            format = format.format,
            components = components,
            subresourceRange = range
        )

        vk_imageview = vulkan.vkCreateImageView(self.vk_device, create, None)
        return ImageView(self, vk_imageview)


    def create_command_pool(self):

        create = vulkan.VkCommandPoolCreateInfo(
            queueFamilyIndex = self.family.family_id,
            flags = 0
        )

        command_pool = vulkan.vkCreateCommandPool(self.vk_device, create, None)
        return CommandPool(self, command_pool)

    def destroy(self):

        vulkan.vkDestroyDevice(self.vk_device, None)


class DeviceQueue():

    def __init__(self, device, queue):

        self.device = device
        self.vk_queue = queue

    def submit(self, command_buffer : CommandBuffer, render_semaphore : VulkanSemaphore, image_semaphore : VulkanSemaphore):

        submit = vulkan.VkSubmitInfo(
            pWaitSemaphores = [image_semaphore.vk_semaphore],
            pWaitDstStageMask = [vulkan.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT],
            pCommandBuffers = [command_buffer.vk_command_buffer],
            pSignalSemaphores = [render_semaphore.vk_semaphore]
        )

        vulkan.vkQueueSubmit(self.vk_queue, 1, submit, None)

    def present(self, swapchain, render_semaphore : VulkanSemaphore, image_index):

        present = vulkan.VkPresentInfoKHR(
            pWaitSemaphores = [render_semaphore.vk_semaphore],
            pSwapchains = [swapchain.vk_swapchain],
            pImageIndices = [image_index]
        )

        self.device.ext.vkQueuePresentKHR(self.vk_queue, present)

