cd grpc
python -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/messages.proto
python -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/services.proto
fix imports for services_pb2_grpc.py:
    replace: import messages_pb2 as messages__pb2
    to: from . import messages_pb2 as messages__pb2