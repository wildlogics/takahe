import logging

import vulkan

from takahe.base.singleton import environment
from takahe.base.lib_glfw import VulkanSurface
from takahe.base.types import VulkanInstance as Interface, PhysicalDevice as PhysicalDeviceInterface
from takahe.compositor.device import LogicalDevice
#from takahe.compositor.ext_swapchain import Swapchain
from takahe.compositor.image import ImageView


class VulkanFramework():

    def __init__(self, logger = None, instance_extensions = None):

        self.logger = logger if logger else logging.getLogger(__name__)
        self.required_extensions = [] if instance_extensions is None else instance_extensions

        self.logger.info("Available Instance Extensions:")
        for ext in self.extensions:
            self.logger.info(f" · {ext.extensionName}")

    def init(self, name, version, init_debugger = None):

        self.vulkan_instance = VulkanInstance(name, version, init_debugger, self.required_extensions)
        self.physical_device = self.get_physical_device()

        if self.physical_device == vulkan.VK_NULL_HANDLE:
            raise RuntimeError("Unable to find a valid vulkan GPU device")

        else:

            properties = self.physical_device.properties()
            features = self.physical_device.features()
            self.logger.info("Device: %s" % properties.deviceName)
            if properties.deviceType == vulkan.VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU:
                self.logger.info("I like this GPU :)")
            self.logger.info("MaxImageDimension2D: %s" % properties.limits.maxImageDimension2D)
            self.logger.info("GeometryShader: %s" % features.geometryShader)

            self.logger.info("Available Device Extensions:")
            for ext in self.physical_device.list_extensions():
                self.logger.info(f" · {ext.extensionName}")

        self.logger.info("QueueFamilies:")
        for qf in self.physical_device.queue_families():

            self.logger.info(f' · {qf}')

        # self.swapchain = Swapchain(self.physical_device, self.surface)
        # self.logger.info("Device Surface Capabilities:")
        # print(self.swapchain.capabilities())
        #
        # device_extensions = []
        # device_extensions.extend(self.swapchain.extensions)
        # self.device = self.physical_device.create_device(self.vulkan_instance, self.surface, device_extensions)
        # # self.queue = self.device.get_queue()
        #
        # self.swapchain.init(self.device)
        #
        # format = self.swapchain.surface_format
        # self.images = [ImageView(self.device, image, format) for image in self.swapchain.chain_images]

    def set_surface(self, surface : VulkanSurface):

        self.surface = surface

    def destroy(self):

        # for image in self.images: image.destroy()
        # self.swapchain.destroy()
        # self.device.destroy()
        self.surface.destroy()
        self.vulkan_instance.destroy()

    @property
    def extensions(self):

        return vulkan.vkEnumerateInstanceExtensionProperties(None)

    def get_physical_device(self):

        instance = self.vulkan_instance.vk_instance
        devices = vulkan.vkEnumeratePhysicalDevices(instance)
        return PhysicalDevice(devices[0])



class VulkanInstance(Interface):

    def __init__(self, name, version, init_debugger, instance_extensions):

        self.init(name, version, init_debugger, instance_extensions)
        self.ext = InstanceProcAddr(self.vk_instance)

    def init(self, name, version, init_debugger, instance_extensions):

        app_info = vulkan.VkApplicationInfo(
            pApplicationName=name,
            applicationVersion=vulkan.VK_MAKE_VERSION(version[0], version[1], version[2]),
            apiVersion=vulkan.VK_API_VERSION_1_0
        )

        extensions = []
        self.layers = []
        init_debugger_info = None

        if init_debugger:

            extensions.append(vulkan.VK_EXT_DEBUG_UTILS_EXTENSION_NAME)
            self.layers.extend(init_debugger.LAYERS)
            init_debugger_info = init_debugger.info

        instance_info = vulkan.VkInstanceCreateInfo(
            pApplicationInfo = app_info,
            ppEnabledExtensionNames = instance_extensions + extensions,
            ppEnabledLayerNames = self.layers,
            pNext = init_debugger_info
        )

        self.vk_instance = vulkan.vkCreateInstance(instance_info, None)


    def destroy(self):

        vulkan.vkDestroyInstance(self.vk_instance, None)



##/
# Execution of instance extesion functions
#/
class InstanceProcAddr():

    def __init__(self, instance):

        self._instance = instance

    def __getattr__(self, fn):

        if fn in vulkan._vulkan._instance_ext_funcs:
            return vulkan.vkGetInstanceProcAddr(self._instance, fn)
        else:
            super().__getattribute__(fn)



class PhysicalDevice(PhysicalDeviceInterface):

    def __init__(self, vulkan_device):

        self.vk_device = vulkan_device
        self.ext = DeviceProcAddr(self.vk_device)

    def properties(self):

        return vulkan.vkGetPhysicalDeviceProperties(self.vk_device)

    def features(self):

        return vulkan.vkGetPhysicalDeviceFeatures(self.vk_device)

    def list_extensions(self):

        return vulkan.vkEnumerateDeviceExtensionProperties(self.vk_device, None)

    def queue_families(self):

        families = vulkan.vkGetPhysicalDeviceQueueFamilyProperties(self.vk_device)
        return [QueueFamily(idx, qf) for idx,qf in enumerate(families)]

    def create_device(self, surface : VulkanSurface, layers, extensions):

        families = [family for family in self.queue_families() if family.is_graphics]
        families = [family for family in families if family.support_khr(self.vk_device, surface.vk_surface_id)]
        queue = families[0]

        queue_info = vulkan.VkDeviceQueueCreateInfo(
            queueFamilyIndex=queue.family_id,
            queueCount=1,
            pQueuePriorities=[1.0]
        )

        features_info = vulkan.VkPhysicalDeviceFeatures()

        device_info = vulkan.VkDeviceCreateInfo(

            pQueueCreateInfos = [queue_info],
            pEnabledFeatures = features_info,
            ppEnabledLayerNames = layers,
            ppEnabledExtensionNames = extensions
        )

        logical_device = vulkan.vkCreateDevice(self.vk_device, device_info, None)
        return LogicalDevice(logical_device, queue)



##/
# Execution of device extension function
#/
class DeviceProcAddr():

    def __init__(self, device):

        self._device = device

    def __getattr__(self, fn):

        if fn in vulkan._vulkan._device_ext_funcs:
            return vulkan.vkGetDeviceProcAddr(self._device, fn)
        else:
            super().__getattribute__(fn)



class QueueFamily():

    def __init__(self, id, queue_family):

        self.family_id = id
        self.vk_family = queue_family

    @property
    def size(self):

        return self.vk_family.queueCount

    @property
    def is_graphics(self):

        return bool(self.vk_family.queueFlags & vulkan.VK_QUEUE_GRAPHICS_BIT)

    @property
    def is_compute(self):
        return bool(self.vk_family.queueFlags & vulkan.VK_QUEUE_COMPUTE_BIT)

    @property
    def is_transfer(self):
        return bool(self.vk_family.queueFlags & vulkan.VK_QUEUE_TRANSFER_BIT)

    @property
    def is_sparse_binding(self):

        return bool(self.vk_family.queueFlags & vulkan.VK_QUEUE_SPARSE_BINDING_BIT)

    def support_khr(self, device, surface):

        instance = environment.base.vulkan.vulkan_instance
        return instance.ext.vkGetPhysicalDeviceSurfaceSupportKHR(device, self.family_id, surface)

    def __str__(self):

        types = ""
        if self.is_graphics: types += "G"
        if self.is_compute: types += "C"
        if self.is_transfer: types += "T"
        if self.is_sparse_binding: types += "S"
        return "QueueFamily #%d %s %d" % (self.family_id, types, self.size)


