#!/usr/bin/python
# -*- coding: utf-8 -*-
import vulkan


class Shader():

    def __init__(self, device, filename):

        self.device = device

        with open(filename, "rb") as spv:

            # spv.seek(0, 2)
            # size = spv.tell()
            # int_size = int(size / 4) + 1
            # self.data = vulkan.ffi.new(f'int[{int_size}]')
            # print(vulkan.ffi.alignof(self.data))
            #
            # spv.seek(0)
            # bytes = vulkan.ffi.cast('char*', self.data)
            # idx = 0
            # while idx < size:
            #     bytes[idx] = spv.read(1)
            #     idx += 1

            self.data = bytes(spv.read())

        self.create_module()

    def create_module(self):

        create = vulkan.VkShaderModuleCreateInfo(
            codeSize = len(self.data),
            pCode = self.data
        )

        self.module = vulkan.vkCreateShaderModule(self.device.vk_device, create, None)

    def destroy(self):

        vulkan.vkDestroyShaderModule(self.device.vk_device, self.module, None)

