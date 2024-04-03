from setuptools import setup, find_packages

setup(
    name='impedance-tube',
    version='1.0',
    packages=find_packages(),
    install_requires=['numpy', 'pyaudio', 'matplotlib', 'pyfirmata2', 'pyautogui', 'scipy'],
)