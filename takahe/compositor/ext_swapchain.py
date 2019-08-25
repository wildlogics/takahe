#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List

import vulkan

from takahe.base.lib_cffi import CustomPointer
from takahe.base.types import VulkanSurface, VulkanInstance, PhysicalDevice
from takahe.compositor.semaphore import VulkanSemaphore
from takahe.compositor.types import Swapchain as Interface
from takahe.compositor.image import ImageView
from takahe.compositor.device import LogicalDevice
from takahe.render import RenderPass

class Framebuffer():

    vk_framebuffer = None

    def __init__(self, device : LogicalDevice, render_pass : RenderPass, extent, image_view : ImageView):

        self.device = device
        self.init(render_pass, extent, image_view)

    def init(self, render_pass : RenderPass, extent, image_view : ImageView):

        images = [image_view.vk_imageview]

        create = vulkan.VkFramebufferCreateInfo(
            renderPass = render_pass.vk_render_pass,
            pAttachments = images,
            width = extent.width,
            height = extent.height,
            layers = 1
        )

        self.vk_framebuffer = vulkan.vkCreateFramebuffer(self.device.vk_device, create, None)

    def destroy(self):

        vulkan.vkDestroyFramebuffer(self.device.vk_device, self.vk_framebuffer, None)



class Swapchain(Interface):

    extensions = [vulkan.VK_KHR_SWAPCHAIN_EXTENSION_NAME]
    _extent_maxint = (2**32) - 1

    def __init__(self, device : PhysicalDevice, surface : VulkanSurface):

        super().__init__()

        self.physical_device = device
        self.surface = surface
        self._capabilities = None

        if not self.is_available():

            raise RuntimeError("swapchain extension not available")

    @property
    def instance(self) -> VulkanInstance:

        return self.surface.instance

    def is_available(self):

        extensions = [ext.extensionName for ext in self.physical_device.list_extensions()]
        return all(ext in extensions for ext in self.extensions)

    def capabilities(self):

        if self._capabilities is None:
            caps = CustomPointer('VkSurfaceCapabilitiesKHR*')
            self.instance.ext.vkGetPhysicalDeviceSurfaceCapabilitiesKHR(self.physical_device.vk_device, self.surface.vk_surface_id, caps.cffi_pointer)
            self._capabilities = caps

        return self._capabilities

        # return self._capabilities
        # caps = self.instance.ext.vkGetPhysicalDeviceSurfaceCapabilitiesKHR(self.physical_device.vk_device, self.surface.vk_surface_id)
        # vulkan.ffi.gc(caps, None)
        # return caps
        #
        # pSurfaceCapabilities = vulkan.ffi.new('VkSurfaceCapabilitiesKHR*')
        # self.instance.ext.vkGetPhysicalDeviceSurfaceCapabilitiesKHR(self.physical_device.vk_device, self.surface.vk_surface_id, pSurfaceCapabilities)
        # self.caps.append(pSurfaceCapabilities)
        # return pSurfaceCapabilities[0]


    @property
    def extent(self):

        caps = self.capabilities()
        current = caps.currentExtent

        if current.width == self._extent_maxint or current.height == self._extent_maxint:
            select = vulkan.vkextent2d(1200, 900)
            select.width = max(caps.minImageExtent.width, min(caps.maxImageExtent.width, select.width))
            select.height = max(caps.minImageExtent.height, min(caps.maxImageExtent.height, select.height))
            return select

        else:
            print(f"Swapchain extent: {current.width}x{current.height}")
            return current

    @property
    def image_count(self):

        caps = self.capabilities()
        ic = caps.minImageCount + 1
        return ic if caps.maxImageCount == 0 else min(ic, caps.maxImageCount)

    def list_formats(self):

        return self.instance.ext.vkGetPhysicalDeviceSurfaceFormatsKHR(self.physical_device.vk_device, self.surface.vk_surface_id)

    @property
    def surface_format(self):

        formats = self.list_formats()
        return formats[0]

    def list_present_modes(self):

        return self.instance.ext.vkGetPhysicalDeviceSurfacePresentModesKHR(self.physical_device.vk_device, self.surface.vk_surface_id)

    @property
    def present_mode(self):

        modes = self.list_present_modes()
        return modes[0]


    def init(self, logical_device : LogicalDevice):

        caps = self.capabilities()
        surface_format = self.surface_format

        create = vulkan.VkSwapchainCreateInfoKHR(
            surface = self.surface.vk_surface_id,
            minImageCount = self.image_count,
            imageFormat = surface_format.format,
            imageColorSpace = surface_format.colorSpace,
            imageExtent = self.extent,
            imageArrayLayers = 1,
            imageUsage = vulkan.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            imageSharingMode = vulkan.VK_SHARING_MODE_EXCLUSIVE,
            preTransform = caps.currentTransform,
            compositeAlpha = vulkan.VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode = self.present_mode,
            clipped = vulkan.VK_TRUE,
            oldSwapchain = vulkan.VK_NULL_HANDLE
        )

        # pswapchain = vulkan.ffi.new('vkswapchainkhr')
        # p_swapchain = vulkan.ffi.new('int *')
        # pswapchain = vulkan.ffi.cast('vkswapchainkhr', p_swapchain)
        self.vk_swapchain = self.instance.ext.vkCreateSwapchainKHR(logical_device.vk_device, create, None)
        self.logical_device = logical_device
        self.chain_images = self.create_images()

    def create_images(self):

        device = self.logical_device
        format = self.surface_format
        imagenes = self.instance.ext.vkGetSwapchainImagesKHR(device.vk_device, self.vk_swapchain)
        opaque = vulkan.ffi.cast('int64_t*', imagenes)
        return [device.create_image_view(opaque[idx], format) for idx in range(len(imagenes))]

    def create_framebuffers(self, render_pass:RenderPass):

        fbs = []

        for image in self.chain_images:
            fbs.append(Framebuffer(self.logical_device, render_pass, self.extent, image))

        return fbs


    def next_image(self, semaphore : VulkanSemaphore):

        _timeout_maxint = (2 ** 64) - 1

        return self.instance.ext.vkAcquireNextImageKHR(
            self.logical_device.vk_device,
            self.vk_swapchain,
            _timeout_maxint,
            semaphore.vk_semaphore,
            None
        )

    def destroy(self):

        # self.framebuffer.destroy()

        list(map(lambda image : image.destroy(), self.chain_images))
        self.instance.ext.vkDestroySwapchainKHR(self.logical_device.vk_device, self.vk_swapchain, None)

