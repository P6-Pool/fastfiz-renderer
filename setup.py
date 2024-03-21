from setuptools import setup, find_packages
from setuptools.command.install import install
import os


class CustomInstall(install):
    def run(self):
        install.run(self)
        compile_protobufs()


def compile_protobufs():
    from grpc_tools import protoc

    proto_dir = "./fastfiz-renderer-protobuffers"
    os.makedirs("fastfiz_renderer/compiled_protos", exist_ok=True)
    protoc.main(
        [
            "--pyi_out=./fastfiz_renderer/compiled_protos",
            "--python_out=./fastfiz_renderer/compiled_protos",
            "--grpc_python_out=./fastfiz_renderer/compiled_protos",
            "--proto_path=" + proto_dir,
            proto_dir + "/api.proto",
        ]
    )


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="fastfiz_renderer",
    version="0.0.1",
    packages=find_packages(),
    license="MIT",
    setup_requires=["grpcio-tools"],
    install_requires=requirements,
    py_modules=["fastfiz_renderer"],
    cmdclass={"install": CustomInstall},
)
