from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='fastfiz_renderer',
    version='0.0.1',
    packages=find_packages(),
    license='MIT',
    install_requires=requirements,
    py_modules=['fastfiz_renderer']
)

# python -m grpc_tools.protoc  --python_out=./fastfiz_renderer/compiled_protos --pyi_out=./fastfiz_renderer/compiled_protos  --grpc_python_out=./fastfiz_renderer/compiled_protos  --proto_path=./protos ./protos/api.proto
# cd py_protos && sed -i '' 's/^(import.pb2)/from . \1/g'.py

