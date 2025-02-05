package com.milikovv.interfacecollector

import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.cancelChildren
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import javax.inject.Inject
import javax.inject.Provider
import javax.inject.Singleton
import kotlin.coroutines.CoroutineContext

@Singleton
class CommandProcessor @Inject constructor(
    private val muxers: Map<String, @JvmSuppressWildcards Provider<Multiplexer>>,
    private val modeCallback: ModeCallbackProvider
) {
    init {
        Log.d(TAG, "on CommandProcessor")
    }

    fun loadMultiplexer(mode : CommandReceiver.SupplyMode) {
        Log.d(TAG, "Loading muxer based on mode \"$mode\"")

        // Stop previous muxer
        if (job?.isActive == true) {
            Log.d(TAG, "Stopping job")
            coroutineContext.cancelChildren()
            Log.d(TAG, "Job stopped")
        }

        Log.d(TAG, "Before starting job")
        // Get and start new muxer
        job = scope.launch {
            Log.d(TAG, "Starting job")
            modeCallback.flow.emit(mode)
            Log.d(TAG, "Getting provider")
            val provider = muxers[mode.name]
            Log.d(TAG, "Getting muxer")
            val muxer = provider!!.get()
            Log.d(TAG, "Setting muxer to work state")
            muxer.work()
            Log.d(TAG, "After muxer.work()")
        }
        Log.d(TAG, "After starting job")
    }


    companion object {
        private val TAG = CommandProcessor::class.java.simpleName

        private val coroutineContext: CoroutineContext = Job()
        private val scope: CoroutineScope = CoroutineScope(coroutineContext)
        private var job : Job? = null
    }
}