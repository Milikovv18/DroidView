package com.milikovv.interfacecollector.dagger

import com.milikovv.interfacecollector.ModeCallbackProvider
import com.milikovv.interfacecollector.ScreenResCallbackProvider
import dagger.Module
import dagger.Provides
import javax.inject.Singleton

@Module
class ModeCallbackModule {
    @Singleton
    @Provides
    fun callbackFlow() : ModeCallbackProvider {
        return ModeCallbackProvider()
    }
}

@Module
class ScreenResCallbackModule {
    @Singleton
    @Provides
    fun callbackFlow() : ScreenResCallbackProvider {
        return ScreenResCallbackProvider()
    }
}
