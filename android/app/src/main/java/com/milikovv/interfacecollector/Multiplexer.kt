package com.milikovv.interfacecollector

import android.util.Log
import com.milikovv.interfacecollector.consumers.Consumer
import com.milikovv.interfacecollector.consumers.RtmpWrapper
import com.milikovv.interfacecollector.suppliers.Supplier
import com.milikovv.interfacecollector.suppliers.accessibility.AccessibilityListener
import com.octiplex.android.rtmp.H264VideoFrame
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.last
import javax.inject.Inject
import javax.inject.Named


interface Multiplexer {
    suspend fun work()

    class VideoDrivenMuxer @Inject constructor(
        private var videoSource: Supplier<H264VideoFrame>,
        @Named("minimal")
        private var metaSource: Supplier<String>,
        private var rtmp: Consumer
    ) : Multiplexer {

        override suspend fun work() {
            videoSource.getHotStream().collect {
                rtmp.consume(it)
                metaSource.getOnce { meta -> meta?.let { rtmp.consume(meta) } }
            }
        }
    }

    class AccessibilityDrivenMuxer @Inject constructor(
        private var videoSource: Supplier<H264VideoFrame>,
        @Named("full")
        private var metaSource: Supplier<String>,
        private var rtmp: Consumer
    ) : Multiplexer {

        override suspend fun work() {
            videoSource.getHotStream().collect {
                rtmp.consume(it)
                metaSource.getOnce { meta -> meta?.let { rtmp.consume(meta) } }
            }
        }
    }

    // Streaming pause, returns immediately
    class StubMuxer @Inject constructor() : Multiplexer {
        override suspend fun work() {
            Log.d(StubMuxer::class.simpleName, "Stub mutex work() called")
        }
    }
}