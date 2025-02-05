package com.milikovv.interfacecollector

import android.content.Context
import android.content.Intent
import android.util.Log
import dagger.android.DaggerBroadcastReceiver
import javax.inject.Inject


class CommandReceiver : DaggerBroadcastReceiver() {
    enum class SupplyMode {
        ACCESSIBILITY_DRIVEN,
        VIDEO_DRIVEN,

        STUB
    }

    // adb shell am broadcast -a com.interfacecollector.intent.COMMAND --es mode "video-driven" -n com.milikovv.interfacecollector/.CommandReceiver

    @Inject
    lateinit var tmpProcessor: CommandProcessor

    override fun onReceive(context: Context?, intent: Intent?) {
        super.onReceive(context, intent)

        if (processor == null) {
            Log.d(TAG, "Replacing processor")
            processor = tmpProcessor
        }

        val mode = intent?.getStringExtra(CONTROL_EXTRA_MODE) ?: return
        Log.d(TAG, "Got mode $mode")

        try {
            processor?.loadMultiplexer(SupplyMode.valueOf(mode))
        } catch (e : IllegalArgumentException) {
            Log.e(TAG, "Got unknown supply mode \"$mode\"")
        }
    }


    companion object {
        val TAG = CommandReceiver::class.simpleName
        const val CONTROL_EXTRA_MODE = "mode"

        // BroadcastReceiver is recreated on each onReceive event, so saving CommandProcessor
        // to actually remain Singleton
        var processor: CommandProcessor? = null
    }
}