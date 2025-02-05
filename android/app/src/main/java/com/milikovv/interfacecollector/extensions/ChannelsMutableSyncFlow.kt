package com.milikovv.interfacecollector.extensions

import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.ClosedReceiveChannelException
import kotlinx.coroutines.channels.ClosedSendChannelException
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.launch
import java.io.Closeable
import java.util.Collections


internal interface SyncFlow<T> : Flow<T>
internal interface MutableSyncFlow<T> : SyncFlow<T> {
    suspend fun emit(value: T)
}


class ChannelsMutableSyncFlow<T> : MutableSyncFlow<T> {

    private var channels = Collections.synchronizedList(mutableListOf<SyncChannel<T>>())

    override suspend fun collect(collector: FlowCollector<T>) {
        createChannel().use { channel ->
            while (true) {
                channel.receive { collector.emit(it) }
            }
        }
    }

    private fun createChannel() =
        SyncChannel(onClose = { channels.remove(it) }).also { channels.add(it) }

    override suspend fun emit(value: T) = coroutineScope {
        synchronized(channels) { channels.forEach { launch { it.send(value) } } }
    }

    private class SyncChannel<T>(
        private val data: Channel<T> = Channel(),
        private val ack: Channel<Unit> = Channel(),
        private val onClose: (SyncChannel<T>) -> Unit
    ) : Closeable {

        suspend fun send(value: T) {
            try {
                data.send(value)
                ack.receive()
            } catch (_: ClosedReceiveChannelException) {} catch (_: ClosedSendChannelException) {}
        }

        suspend fun receive(block: suspend (T) -> Unit) {
            try {
                block(data.receive())
                ack.send(Unit)
            } catch (_: ClosedReceiveChannelException) {} catch (_: ClosedSendChannelException) {}
        }

        override fun close() {
            data.close()
            ack.close()
            onClose(this)
        }
    }
}