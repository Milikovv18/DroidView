package com.milikovv.interfacecollector.dagger

import com.milikovv.interfacecollector.Multiplexer
import com.milikovv.interfacecollector.consumers.Consumer
import com.milikovv.interfacecollector.consumers.RtmpWrapper
import com.milikovv.interfacecollector.suppliers.Supplier
import com.milikovv.interfacecollector.suppliers.accessibility.AccessibilityListener
import com.milikovv.interfacecollector.suppliers.accessibility.serializers.FullAccessibilityListener
import com.milikovv.interfacecollector.suppliers.accessibility.serializers.MinimalAccessibilityListener
import com.milikovv.interfacecollector.suppliers.media_projection.H264Listener
import com.octiplex.android.rtmp.H264VideoFrame
import dagger.Binds
import dagger.Module
import dagger.multibindings.IntoMap
import dagger.multibindings.IntoSet
import dagger.multibindings.StringKey
import javax.inject.Named
import javax.inject.Singleton

@Module
abstract class VideoASRtmpMultiplexerModule {
    @Binds
    abstract fun videoSupplier(supplier : H264Listener) : Supplier<H264VideoFrame>

    @Binds
    abstract fun consumer(consumer : RtmpWrapper) : Consumer
}

@Module(includes = [VideoASRtmpMultiplexerModule::class])
abstract class VideoDrivenMultiplexerModule {
    @Binds @Named("minimal")
    abstract fun accessibilitySupplier(supplier : MinimalAccessibilityListener) : Supplier<String>

    @Singleton
    @Binds @IntoSet
    abstract fun accessibilityChild(child : MinimalAccessibilityListener) : AccessibilityListener

    @Binds @IntoMap @StringKey("VIDEO_DRIVEN")
    abstract fun multiplexer(muxer : Multiplexer.VideoDrivenMuxer) : Multiplexer
}

@Module(includes = [VideoASRtmpMultiplexerModule::class])
abstract class AccessibilityDrivenMultiplexerModule {
    @Binds @Named("full")
    abstract fun accessibilitySupplier(supplier : FullAccessibilityListener) : Supplier<String>

    @Singleton
    @Binds @IntoSet
    abstract fun accessibilityChild(child : FullAccessibilityListener) : AccessibilityListener

    @Binds @IntoMap @StringKey("ACCESSIBILITY_DRIVEN")
    abstract fun multiplexer(muxer : Multiplexer.AccessibilityDrivenMuxer) : Multiplexer
}

@Module(includes = [VideoASRtmpMultiplexerModule::class])
abstract class StubMultiplexerModule {
    @Binds @IntoMap @StringKey("STUB")
    abstract fun multiplexer(muxer : Multiplexer.StubMuxer) : Multiplexer
}
