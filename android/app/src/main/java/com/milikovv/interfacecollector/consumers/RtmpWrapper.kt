package com.milikovv.interfacecollector.consumers

import android.util.Log
import com.octiplex.android.rtmp.H264VideoFrame
import com.octiplex.android.rtmp.RtmpConnectionListener
import com.octiplex.android.rtmp.RtmpMuxer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import java.io.IOException
import java.net.ConnectException
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.concurrent.thread

@Singleton
class RtmpWrapper private constructor() : RtmpConnectionListener, Consumer {
    private lateinit var muxer: RtmpMuxer
    private var isConnected = MutableStateFlow(false)
    private var connectionError: Boolean = false

    constructor(muxer: RtmpMuxer) : this() {
        Log.d(TAG, "on RtmpWrapper")
        this.muxer = muxer

        // Always call start method from a background thread.
        thread {
            this.muxer.start(this, "scrapper", null, null)
        }
    }

    @Synchronized
    override fun consume(data: Any) {
        if (!isConnected.value) {
            throw IOException("Not ready to publish yet")
        }

        when (data) {
            is H264VideoFrame -> muxer.postVideo(data)
            is String -> muxer.sendMetaData(data)
            else -> throw UnsupportedOperationException("Cannot send object of type " +
                    data.javaClass.simpleName)
        }
    }

    fun isAborted() : Boolean {
        return connectionError
    }

    override fun onConnected() {
        Log.d(TAG, "onConnected")
        // Muxer is connected to the RTMP server, you can create a stream to publish data
        thread {
            muxer.createStream("play_path")
        }
    }

    override fun onReadyToPublish() {
        Log.d(TAG, "onReadyToPublish")
        // Muxer is connected to the server and ready to receive data
        isConnected.value = true
    }

    override fun onConnectionError(e: IOException) {
        // Error while connecting to the server
        try {
            throw e
        } catch (e: IOException) {
            Log.e(TAG, "Connection I/O error")
        } catch (e: ConnectException) {
            Log.e(TAG, "Unable to connect")
        } catch (e: com.octiplex.android.rtmp.io.ServerException) {
            Log.e(TAG, "Stop client")
        } finally {
            isConnected.value = false
            connectionError = true
        }
    }

    fun waitForConnection() {
        runBlocking {
            isConnected.first { it }
        }
    }


    companion object {
        val TAG: String = Companion::class.java.simpleName
    }
}