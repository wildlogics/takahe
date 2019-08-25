#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from takahe.app import VulkanApplication
from takahe.base import Configuration

if __name__== "__main__":

    config = Configuration(debug = True)
    app = VulkanApplication(config)

    try:

        app.run()

    except Exception as e:

        print("\n### ERROR ###\n###")

        if hasattr(e, 'message'):
            print("### %s" % e.message)
        else:
            print("### %s" % e)

        print("###\n", flush=True)
        sys.stderr.flush()
        raise e
        exit(1)