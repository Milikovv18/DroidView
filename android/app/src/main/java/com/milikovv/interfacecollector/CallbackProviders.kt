package com.milikovv.interfacecollector

import android.graphics.Point
import com.milikovv.interfacecollector.extensions.ChannelsMutableSyncFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ModeCallbackProvider @Inject constructor() {
    val flow = ChannelsMutableSyncFlow<CommandReceiver.SupplyMode>()
}

@Singleton
class ScreenResCallbackProvider @Inject constructor() {
    val flow = ChannelsMutableSyncFlow<Point>()
}
