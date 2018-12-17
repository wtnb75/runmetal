import os
# import subprocess
import objc as _objc
# from CoreFoundation import *

# basepath = subprocess.run(["xcode-select", "-p"],
#                          capture_output=True).stdout.decode("utf8").strip()
# macossdk="/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"
basepath = "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer"
macossdk = os.path.join(basepath, "SDKs", "MacOSX.sdk")
name = "Metal"

p = os.path.join(macossdk, "System", "Library",
                 "Frameworks", name + ".framework")

if not os.path.isdir(p):
    raise Exception("framework path does not exists: " + p)

__bundle__ = _objc.initFrameworkWrapper(
    name, frameworkIdentifier="com.apple." + name,
    frameworkPath=_objc.pathForFramework(p), globals=globals())
