package com.milikovv.interfacecollector.dagger

import android.media.MediaCodec
import android.view.Surface
import dagger.Module
import dagger.Provides
import javax.inject.Singleton


@Module
class MediaCodecSurfaceModule {
    @Singleton
    @Provides
    fun surface() : Surface {
        return MediaCodec.createPersistentInputSurface()
    }
}