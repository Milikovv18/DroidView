package com.milikovv.interfacecollector.consumers

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.runBlocking
import java.io.DataOutputStream
import java.net.Socket
import kotlin.concurrent.thread
import kotlin.coroutines.CoroutineContext

class TcpClient(host: String, port: Int) : Consumer {
    private var client: Socket = Socket(host, port)
    private var outStream: DataOutputStream = DataOutputStream(client.getOutputStream())
    private val channel = Channel<Any>(Channel.UNLIMITED)

    init {
        thread {
            sendContinuously()
        }
    }

    override fun consume(data: Any) {
        // Pure send() doesn't really block noticeably
        runBlocking {
            channel.send(data)
        }
    }

    private fun sendContinuously() {
        runBlocking {
            for (data in channel) {
                when (data) {
                    is ByteArray -> outStream.write(data)
                    is Int -> outStream.writeInt(data)
                    else -> throw UnsupportedOperationException("Cannot send object of type " +
                            data.javaClass.simpleName)
                }
            }
        }
    }
}
