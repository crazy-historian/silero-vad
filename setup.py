from setuptools import setup
from pathlib import Path

project_path = Path(__file__).parent

README = str(Path(f'{project_path}/README.md'))
with open(README, encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='silero_vad_simplified',
    version='0.1.1',    
    description='This is a fork of silero-vad repository with a bit refactored code for simpler installation.',
    long_description=long_description,
    license='MIT License',
    long_desctiption_content_type='text/markdown',
    url='https://github.com/crazy-historian/silero-vad',
    author='Maxim Zaitsev',
    author_email='zaitsev808@mail.ru',
    packages=['silero_vad', 'silero_vad/files'],
    package_data={
        'silero_vad/files': ['lang_dict_95.json', 'lang_dict_95.json', 'silero_vad.jit', 'silero_vad.onnx']},
    include_package_data=True,
    install_requires=[
        'numpy',
        'torch',
        'torchaudio',
        'onnxruntime'
        ],
)
