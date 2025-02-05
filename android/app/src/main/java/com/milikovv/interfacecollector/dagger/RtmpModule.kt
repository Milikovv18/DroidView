package com.milikovv.interfacecollector.dagger

import com.milikovv.interfacecollector.consumers.RtmpWrapper
import com.milikovv.interfacecollector.consumers.TcpClient
import com.octiplex.android.rtmp.RtmpMuxer
import dagger.Component
import dagger.Module
import dagger.Provides
import javax.inject.Singleton

@Module
class LocalhostRtmpModule {
    @Singleton
    @Provides
    fun rtmpConsumer() : RtmpWrapper {
        val muxer = RtmpWrapper(
            RtmpMuxer("127.0.0.1", 1935) { System.currentTimeMillis() }
        )
        muxer.waitForConnection()
        return muxer
    }
}
