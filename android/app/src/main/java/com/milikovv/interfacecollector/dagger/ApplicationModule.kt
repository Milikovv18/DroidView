package com.milikovv.interfacecollector.dagger

import com.milikovv.interfacecollector.CommandReceiver
import com.milikovv.interfacecollector.UiScrapper
import com.milikovv.interfacecollector.suppliers.accessibility.AccessibilityServiceService
import com.milikovv.interfacecollector.suppliers.media_projection.MediaProjectionService
import dagger.BindsInstance
import dagger.Component
import dagger.Module
import dagger.android.ContributesAndroidInjector
import dagger.android.support.AndroidSupportInjectionModule
import javax.inject.Singleton


@Module
internal abstract class AccessibilityServiceModule {
    @ContributesAndroidInjector
    abstract fun contributeAccessibility(): AccessibilityServiceService?
}

@Module
internal abstract class ScreenCaptureServiceModule {
    @ContributesAndroidInjector
    abstract fun contributeScreenCapture(): MediaProjectionService?
}

@Module
internal abstract class CommandReceiverModule {
    @ContributesAndroidInjector
    abstract fun contributeCommandReceiver(): CommandReceiver?
}


@Component(modules = [
    // Android system classes
    AndroidSupportInjectionModule::class,
    AccessibilityServiceModule::class,
    ScreenCaptureServiceModule::class,
    CommandReceiverModule::class,

    // Multiplexers
    VideoDrivenMultiplexerModule::class,
    AccessibilityDrivenMultiplexerModule::class,
    StubMultiplexerModule::class,

    // Converters
    ScreenResCallbackModule::class,
    MediaCodecSurfaceModule::class,

    // Network
    LocalhostRtmpModule::class
])
@Singleton
interface AppComponent {
    @Component.Builder
    interface Builder {
        @BindsInstance
        fun application(application: UiScrapper?): Builder?

        fun build(): AppComponent?
    }

    fun inject(app: UiScrapper?)
}