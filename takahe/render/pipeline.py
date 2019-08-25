#!/usr/bin/python
# -*- coding: utf-8 -*-
import vulkan

from takahe.commands.types import CommandBuffer
from takahe.render.types import Pipeline as Interface


class PipelineLayout():

    def __init__(self, device, layout):

        self.device = device
        self.vk_layout = layout

    def destroy(self):

        vulkan.vkDestroyPipelineLayout(self.device.vk_device, self.vk_layout, None)


class GraphicsPipeline(Interface):

    def __init__(self, device, extent, render_pass):

        self.device = device
        self.extent = extent
        self.render_pass = render_pass
        self.shader_modules = []

        print(f"Pipeline extent: {self.extent.width}x{self.extent.height}")

        create_layout = vulkan.VkPipelineLayoutCreateInfo(
            pSetLayouts = None,
            pPushConstantRanges = None,
        )

        vk_layout = vulkan.vkCreatePipelineLayout(device.vk_device, create_layout, None)
        self.layout = PipelineLayout(self.device, vk_layout)

    def put_shader(self, shader, stage):

        info = vulkan.VkPipelineShaderStageCreateInfo(
            stage = stage,
            module = shader.module,
            pName = "main"
        )

        self.shader_modules.append(info)

    def put_vertex_shader(self, shader):

        self.put_shader(shader, vulkan.VK_SHADER_STAGE_VERTEX_BIT)

    def put_fragment_shader(self, shader):

        self.put_shader(shader, vulkan.VK_SHADER_STAGE_FRAGMENT_BIT)



    def brew(self):

        vertex_info = vulkan.VkPipelineVertexInputStateCreateInfo(
            pVertexBindingDescriptions=None,
            pVertexAttributeDescriptions=None,
        )

        input_assembly_info = vulkan.VkPipelineInputAssemblyStateCreateInfo(
            topology = vulkan.VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST,
            primitiveRestartEnable = vulkan.VK_FALSE
        )

        print(f"Viewport extent: {self.extent.width}x{self.extent.height}")
        viewport = vulkan.VkViewport(
            x = 0.0,
            y = 0.0,
            width = self.extent.width,
            height = self.extent.height,
            minDepth = 0.0,
            maxDepth = 1.0
        )

        scissor = vulkan.VkRect2D(
            offset = vulkan.VkOffset2D(0,0),
            extent = self.extent
        )

        viewport_state = vulkan.VkPipelineViewportStateCreateInfo(
            pViewports = [viewport],
            pScissors = [scissor]
        )

        rasterizer = vulkan.VkPipelineRasterizationStateCreateInfo(
            depthClampEnable = vulkan.VK_FALSE,
            rasterizerDiscardEnable = vulkan.VK_FALSE,
            polygonMode = vulkan.VK_POLYGON_MODE_FILL,
            lineWidth = 1.0,
            cullMode = vulkan.VK_CULL_MODE_BACK_BIT,
            frontFace = vulkan.VK_FRONT_FACE_CLOCKWISE,
            depthBiasEnable = vulkan.VK_FALSE,
            depthBiasConstantFactor = 0.0,
            depthBiasClamp = 0.0,
            depthBiasSlopeFactor = 0.0,
        )

        multisampling = vulkan.VkPipelineMultisampleStateCreateInfo(
            sampleShadingEnable = vulkan.VK_FALSE,
            rasterizationSamples = vulkan.VK_SAMPLE_COUNT_1_BIT,
            minSampleShading = 1.0,
            pSampleMask = None,
            alphaToCoverageEnable = vulkan.VK_FALSE,
            alphaToOneEnable = vulkan.VK_FALSE
        )

        depth_stencil = vulkan.VkPipelineDepthStencilStateCreateInfo()

        colorblend = vulkan.VkPipelineColorBlendAttachmentState(
            colorWriteMask = vulkan.VK_COLOR_COMPONENT_R_BIT | vulkan.VK_COLOR_COMPONENT_G_BIT | vulkan.VK_COLOR_COMPONENT_B_BIT | vulkan.VK_COLOR_COMPONENT_A_BIT,
            blendEnable = vulkan.VK_FALSE,
            srcColorBlendFactor = vulkan.VK_BLEND_FACTOR_ONE,
            dstColorBlendFactor = vulkan.VK_BLEND_FACTOR_ZERO,
            colorBlendOp = vulkan.VK_BLEND_OP_ADD,
            srcAlphaBlendFactor = vulkan.VK_BLEND_FACTOR_ONE,
            dstAlphaBlendFactor = vulkan.VK_BLEND_FACTOR_ZERO,
            alphaBlendOp = vulkan.VK_BLEND_OP_ADD,
        )

        colorblending = vulkan.VkPipelineColorBlendStateCreateInfo(
            logicOpEnable = vulkan.VK_FALSE,
            logicOp = vulkan.VK_LOGIC_OP_COPY,
            pAttachments = [colorblend],
            blendConstants = [0.0, 0.0, 0.0, 0.0]
        )

        dynamic_state = vulkan.VkPipelineDynamicStateCreateInfo(
            pDynamicStates = [vulkan.VK_DYNAMIC_STATE_VIEWPORT, vulkan.VK_DYNAMIC_STATE_LINE_WIDTH]
        )

        create_pipeline = vulkan.VkGraphicsPipelineCreateInfo(
            pStages = self.shader_modules,
            pVertexInputState = vertex_info,
            pInputAssemblyState = input_assembly_info,
            pViewportState = viewport_state,
            pRasterizationState = rasterizer,
            pMultisampleState = multisampling,
            pDepthStencilState = None,
            pColorBlendState = colorblending,
            pDynamicState = None,
            layout = self.layout.vk_layout,
            renderPass = self.render_pass.vk_render_pass,
            subpass = 0,
            basePipelineHandle = vulkan.VK_NULL_HANDLE,
            basePipelineIndex = -1
        )

        self.vk_pipelines = vulkan.vkCreateGraphicsPipelines(self.device.vk_device, vulkan.VK_NULL_HANDLE, 1, [create_pipeline], None)



    def destroy(self):

        vulkan.vkDestroyPipeline(self.device.vk_device, self.vk_pipelines[0], None)
        self.layout.destroy()
