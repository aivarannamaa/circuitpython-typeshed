import shutil
import os.path
import sys
import subprocess
import tarfile
import fileinput

CP_STUBS_VERSION = "9.2.7"
MP_STUBS_VERSION = "1.25.0.post1"

if os.path.exists("src"):
    shutil.rmtree("src")
os.makedirs("src")

# I'm keeping the copy of input stubs, to be able to monitor the changes also in the parts not included in src

input_mp_stubs_path = f"input_micropython_stubs"
if os.path.exists(input_mp_stubs_path):
    shutil.rmtree(input_mp_stubs_path)

subprocess.run([sys.executable, "-m", "pip", "install",
                "--target", input_mp_stubs_path,
                "--no-user",
                f"micropython-rp2-stubs=={MP_STUBS_VERSION}"])

input_cp_stubs_path = f"input_circuitpython_stubs"
if os.path.exists(input_cp_stubs_path):
    shutil.rmtree(input_cp_stubs_path)

subprocess.run([sys.executable, "-m", "pip", "download",
                "-d", ".",
                "--no-binary=:all:",
                f"circuitpython-stubs=={CP_STUBS_VERSION}"])

tar_path = f"circuitpython_stubs-{CP_STUBS_VERSION}.tar.gz"
with tarfile.open(tar_path, 'r:gz') as tar:
    tar.extractall(path=".")
os.remove(tar_path)

os.rename(f"circuitpython_stubs-{CP_STUBS_VERSION}", input_cp_stubs_path)


input_cp_modules = [name for name in os.listdir(input_cp_stubs_path)
                    if os.path.isdir(os.path.join(input_cp_stubs_path, name))]

required_cp_modules = """
__future__        busdisplay        math              struct
__main__          busio             mdns              supervisor
_asyncio          codeop            memorymap         synthio
_bleio            collections       microcontroller   sys
_eve              countio           micropython       terminalio
_pixelmap         cyw43             msgpack           tilepalettemapper
adafruit_bus_device                 digitalio         neopixel_write    time
adafruit_bus_device.i2c_device      displayio         nvm               touchio
adafruit_bus_device.spi_device      epaperdisplay     onewireio         traceback
adafruit_pixelbuf errno             os                ulab
aesio             floppyio          paralleldisplay   ulab.numpy
alarm             fontio            paralleldisplaybus                  ulab.numpy.fft
analogbufio       fourwire          pulseio           ulab.numpy.linalg
analogio          framebufferio     pwmio             ulab.scipy
array             gc                qrio              ulab.scipy.linalg
atexit            getpass           rainbowio         ulab.scipy.optimize
audiobusio        gifio             random            ulab.scipy.signal
audiocore         hashlib           re                ulab.scipy.special
audiomixer        i2cdisplaybus     rgbmatrix         ulab.utils
audiomp3          i2ctarget         rotaryio          usb_cdc
audiopwmio        imagecapture      rp2pio            usb_hid
binascii          io                rtc               usb_midi
bitbangio         ipaddress         sdcardio          usb_video
bitmapfilter      jpegio            select            vectorio
bitmaptools       json              sharpdisplay      warnings
bitops            keypad            socketpool        watchdog
board             keypad_demux      ssl               wifi
builtins          locale            storage           zlib
""".strip().split()

cp_toplevel_modules = list(sorted({module.split(".")[0] for module in required_cp_modules}))
print(f"{cp_toplevel_modules=}")

# Copy MicroPython's stdlib
for name in ["stdlib", "stubs"]:
    full_path = os.path.join(input_mp_stubs_path, name)
    shutil.copytree(full_path, os.path.join("src", name))

# Copy MicroPython's helpers under stdlib (don't know why they are outside stlib in the input)
shutil.copytree(os.path.join("input_micropython_stubs", "_mpy_shed"), "src/stdlib/_mpy_shed")

# Copy MicroPython's stubs under stdlib
for name in os.listdir(input_mp_stubs_path):
    full_path = os.path.join(input_mp_stubs_path, name)
    if name.endswith(".pyi"):
        shutil.copy(full_path, f"src/stdlib/{name}")

# delete MicroPython-specific pyi files
mypy_required = {
    "builtins",
    "typing",
    "types",
    "typing_extensions",
    "mypy_extensions",
    "_typeshed",
    "_collections_abc",
    "collections",
    "collections.abc",
    "sys",
    "abc",
}
for name in os.listdir("src/stdlib"):
    if name.endswith(".pyi") and name.removesuffix(".pyi") not in cp_toplevel_modules and name.removesuffix(".pyi") not in mypy_required:
        os.remove(os.path.join("src", "stdlib", name))

# Copy CircuitPython stubs over MicroPython ones
for name in os.listdir(input_cp_stubs_path):
    if os.path.exists(os.path.join(input_cp_stubs_path, name, "__init__.pyi")):
        dest = os.path.join("src", "stdlib", name)
        if os.path.exists(dest):
            print("Removing existing", name)
            shutil.rmtree(dest)
        shutil.copytree(os.path.join(input_cp_stubs_path, name), f"src/stdlib/{name}")

# delete plain pyi-files, which have corresponding package
for name in os.listdir("src/stdlib"):
    if name.endswith(".pyi") and os.path.exists(os.path.join("src", "stdlib", name.removesuffix(".pyi"), "__init__.pyi")):
        os.remove(os.path.join("src", "stdlib", name))



# merge MicroPython's __builtins__.pyi with builtins.pyi
with open("src/stdlib/builtins.pyi", "a", encoding="utf-8") as f1:
    with open(os.path.join(input_mp_stubs_path, "__builtins__.pyi"), "r", encoding="utf-8") as f2:
        f1.write("\n\n")
        f1.write(f2.read())

# copy board_definitions and board-setter and tweak it to be usable in changed directory
shutil.copytree(f"{input_cp_stubs_path}/board_definitions", "src/board_definitions")
shutil.copytree(f"{input_cp_stubs_path}/circuitpython_setboard", "src/circuitpython_setboard")

with fileinput.FileInput("src/circuitpython_setboard/__init__.py", inplace=True) as fp:
        for line in fp:
            if 'resources.files("board-stubs")' in line:
                line = line.replace("board-stubs", "stdlib.board")
            print(line, end="")
