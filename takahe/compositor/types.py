#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Any

from takahe.base.types import BaseEnvironment, VulkanInstance, LogicalDevice, PhysicalDevice, VulkanSurface
from takahe.base.types import VulkanObject


class DeviceQueue():

    vk_queue : Any

class LogicalDevice(LogicalDevice):

    vk_device : Any
    queues : List[DeviceQueue]

class Swapchain(VulkanObject):

    surface : VulkanSurface
    instance : VulkanInstance
    physical_device : PhysicalDevice
    extensions : List[str]
    logical_device : LogicalDevice
    surface_format : Any
    extent : Any
    chain_images : List[Any]

class FrameBuffer():

    vk_framebuffer : Any

class Shader():

    device: LogicalDevice
    module: Any

class GraphicsPipeline():

    shader_modules : List[Shader]

class PipelineLayout():

    vk_layout : Any
    device : LogicalDevice
    pipelines : List[GraphicsPipeline]


class Compositor():

    base : BaseEnvironment
    device : LogicalDevice
    swapchain : Swapchain
