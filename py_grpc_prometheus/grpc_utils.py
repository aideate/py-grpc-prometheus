import grpc


UNARY = "UNARY"
SERVER_STREAMING = "SERVER_STREAMING"
CLIENT_STREAMING = "CLIENT_STREAMING"
BIDI_STREAMING = "BIDI_STREAMING"
UNKNOWN = "UNKNOWN"


def get_method_type(request_streaming: bool, response_streaming: bool):
    """
    Infers the method type from if the request or the response is streaming.

    # The Method type is coming from:
    # https://grpc.io/grpc-java/javadoc/io/grpc/MethodDescriptor.MethodType.html
    """
    if request_streaming and response_streaming:
        return BIDI_STREAMING
    elif request_streaming and not response_streaming:
        return CLIENT_STREAMING
    elif not request_streaming and response_streaming:
        return SERVER_STREAMING
    return UNARY


def split_method_call(handler_call_details: grpc.HandlerCallDetails):
    """
    Infers the grpc service and method name from the handler_call_details.
    """

    # e.g. /package.ServiceName/MethodName
    parts = handler_call_details.method.split("/")
    if len(parts) < 3:
        return "", "", False


def split_method_call(handler_call_details):
  """
  Infers the grpc service and method name from the handler_call_details.
  """

  # e.g. /package.ServiceName/MethodName
  parts = handler_call_details.method.split("/")
  if len(parts) < 3:
    return "", "", False

  grpc_service_name, grpc_method_name = parts[1:3]
  return grpc_service_name, grpc_method_name, True


def wrap_rpc_behavior(handler, fn):
  """Returns a new rpc handler that wraps the given function"""
  if handler is None:
    return None

  if handler.request_streaming and handler.response_streaming:
    behavior_fn = handler.stream_stream
    handler_factory = grpc.stream_stream_rpc_method_handler
  elif handler.request_streaming and not handler.response_streaming:
    behavior_fn = handler.stream_unary
    handler_factory = grpc.stream_unary_rpc_method_handler
  elif not handler.request_streaming and handler.response_streaming:
    behavior_fn = handler.unary_stream
    handler_factory = grpc.unary_stream_rpc_method_handler
  else:
    behavior_fn = handler.unary_unary
    handler_factory = grpc.unary_unary_rpc_method_handler
  return handler_factory(
      fn(behavior_fn, handler.request_streaming, handler.response_streaming),
      request_deserializer=handler.request_deserializer,
      response_serializer=handler.response_serializer)


def compute_error_code(grpc_exception):
  if isinstance(grpc_exception, grpc.Call):
    return grpc_exception.code()

  return grpc.StatusCode.UNKNOWN
