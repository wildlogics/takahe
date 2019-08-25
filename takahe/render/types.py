#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Any, List

from takahe.compositor.types import Compositor, LogicalDevice


class RenderPass:
    pass

class Shader:

    device: LogicalDevice
    module: Any


class Pipeline:

    device : LogicalDevice
    extent : Any
    render_pass : RenderPass
    shader_modules = List[Shader]
    vk_pipelines : Any

class Render():

    compositor : Compositor
    renderpass : RenderPass
    pipeline : Pipeline