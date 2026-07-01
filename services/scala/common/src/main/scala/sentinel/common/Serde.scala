package sentinel.common

import zio.kafka.serde.*

object ProtobufSerde:
  def serde[T](parse: Array[Byte] => T, serialize: T => Array[Byte]): Serde[Any, T] =
    Serde.byteArray.inmap(parse)(serialize)
