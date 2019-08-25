#!/usr/bin/python
# -*- coding: utf-8 -*-
import vulkan

from takahe.commands.types import CommandBuffer
from takahe.compositor.types import FrameBuffer
from takahe.render.types import RenderPass as Interface

class RenderPass(Interface):

    def __init__(self, device, format, extent):

        self.device = device

        color_attachment = vulkan.VkAttachmentDescription(
            format = format,
            samples = vulkan.VK_SAMPLE_COUNT_1_BIT,
            loadOp = vulkan.VK_ATTACHMENT_LOAD_OP_CLEAR,
            storeOp = vulkan.VK_ATTACHMENT_STORE_OP_STORE,
            stencilLoadOp = vulkan.VK_ATTACHMENT_LOAD_OP_DONT_CARE,
            stencilStoreOp = vulkan.VK_ATTACHMENT_STORE_OP_DONT_CARE,
            initialLayout = vulkan.VK_IMAGE_LAYOUT_UNDEFINED,
            finalLayout = vulkan.VK_IMAGE_LAYOUT_PRESENT_SRC_KHR

        )

        color_attachment_ref = vulkan.VkAttachmentReference(
            attachment = 0,
            layout = vulkan.VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,

        )

        subpass = vulkan.VkSubpassDescription(
            pipelineBindPoint = vulkan.VK_PIPELINE_BIND_POINT_GRAPHICS,
            pColorAttachments = [color_attachment_ref]
        )

        dependency = vulkan.VkSubpassDependency(
            dstSubpass = 0,
            srcStageMask = vulkan.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            srcAccessMask = 0,
            dstStageMask = vulkan.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            dstAccessMask = vulkan.VK_ACCESS_COLOR_ATTACHMENT_READ_BIT | vulkan.VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT
        )

        render_pass_info = vulkan.VkRenderPassCreateInfo(
            pAttachments = [color_attachment],
            pSubpasses = [subpass],
            pDependencies = [dependency]
        )

        self.vk_render_pass = vulkan.vkCreateRenderPass(device.vk_device, render_pass_info, None)
        self.extent = extent

    def begin(self, command_buffer : CommandBuffer, frame_buffer : FrameBuffer):

        area = vulkan.VkRect2D(
            offset = vulkan.VkOffset2D(0, 0),
            extent = self.extent
        )


        color = vulkan.VkClearColorValue([0.0, 0.0, 0.0, 0.0],[0, 0, 0, 0],[0, 0, 0, 0])
        stencil = vulkan.VkClearDepthStencilValue(0.0, 1)
        clear = vulkan.VkClearValue(
            color = color,
            depthStencil = stencil
        )

        begin = vulkan.VkRenderPassBeginInfo(
            renderPass = self.vk_render_pass,
            framebuffer = frame_buffer.vk_framebuffer,
            renderArea = area,
            pClearValues = [clear]
        )

        vulkan.vkCmdBeginRenderPass(command_buffer.vk_command_buffer, begin, vulkan.VK_SUBPASS_CONTENTS_INLINE)

    def end(self, command_buffer : CommandBuffer):

        vulkan.vkCmdEndRenderPass(command_buffer.vk_command_buffer)

    def destroy(self):

        vulkan.vkDestroyRenderPass(self.device.vk_device, self.vk_render_pass, None)
