#!/usr/bin/python
# -*- coding: utf-8 -*-
from takahe.compositor.semaphore import VulkanSemaphore
from takahe.compositor.types import Compositor
from takahe.render.pipeline import GraphicsPipeline
from takahe.render.renderpass import RenderPass
from takahe.render.shader import Shader
from takahe.render.types import Render as Interface

class Render(Interface):

    def __init__(self, comp : Compositor):

        self.comp = comp

    def init(self):

        format = self.comp.swapchain.surface_format.format
        self.renderpass = RenderPass(self.comp.device, format, self.comp.swapchain.extent)

        self.pipeline = GraphicsPipeline(self.comp.device, self.comp.swapchain.extent, self.renderpass)

        self.shaders = []

        shader = Shader(self.comp.device, 'data/shaders/frag.spv')
        self.shaders.append(shader)
        self.pipeline.put_fragment_shader(shader)

        shader = Shader(self.comp.device, 'data/shaders/vert.spv')
        self.pipeline.put_vertex_shader(shader)
        self.shaders.append(shader)

        self.pipeline.brew()
        # self.vulkan.swapchain.create_framebuffer(self.vulkan.device)

        self.framebuffers = self.comp.swapchain.create_framebuffers(self.renderpass)

        self.commandpool = self.comp.device.create_command_pool()
        self.commandbuffers = self.commandpool.create_buffers(len(self.comp.swapchain.chain_images))


    def render(self):

        for idx, commandbuffer in enumerate(self.commandbuffers):

            commandbuffer.begin()
            self.renderpass.begin(commandbuffer, self.framebuffers[idx])

            commandbuffer.bind(self.pipeline)
            commandbuffer.draw()

            self.renderpass.end(commandbuffer)
            commandbuffer.end()

        self.drawframe()

    def drawframe(self):

        render_sem = VulkanSemaphore(self.comp.device)
        image_available_sem = VulkanSemaphore(self.comp.device)

        next_image_idx = self.comp.swapchain.next_image(image_available_sem)
        command_buffer = self.commandbuffers[next_image_idx]
        self.comp.device.graphics_queue.submit(command_buffer, render_sem, image_available_sem)
        self.comp.device.present_queue.present(self.comp.swapchain, render_sem, next_image_idx)


    def clean(self):

        self.commandpool.destroy()
        list(map(lambda fb: fb.destroy(), self.framebuffers))
        list(map(lambda s : s.destroy(), self.shaders))
        self.pipeline.destroy()
        self.renderpass.destroy()