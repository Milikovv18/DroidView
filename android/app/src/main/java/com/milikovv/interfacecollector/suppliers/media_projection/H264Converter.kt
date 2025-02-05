package com.milikovv.interfacecollector.suppliers.media_projection

import android.graphics.Point
import android.media.MediaCodec
import android.media.MediaCodecInfo
import android.media.MediaFormat
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.Surface
import com.milikovv.interfacecollector.ScreenResCallbackProvider
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onEach
import java.io.IOException
import javax.inject.Inject
import kotlin.coroutines.CoroutineContext


class H264Converter @Inject constructor(
    private val surface: Surface,
    screenResCallback: ScreenResCallbackProvider
) {
    private var screenResCallbackContainer: ScreenResCallbackProvider = screenResCallback
    private var encoder = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_VIDEO_AVC)
    private var listener: H264Listener? = null
    private var screenRes: Point? = null
    private var isEncoderActive = false

    private val coroutineContext: CoroutineContext = Job()
    private val scope: CoroutineScope = CoroutineScope(coroutineContext)

    init {
        screenResCallbackContainer.flow.onEach { res -> callbackScreenResChanged(res) }
            .catch { cause -> Log.e(TAG, "Exception: $cause") }
            .launchIn(scope)
    }

    fun setListener(listener : H264Listener) {
        this.listener = listener
        encoder.setCallback(this.listener)
        //listener.getHotStream().subscriptionCount
        //    .map { count -> count > 0 }
        //    .distinctUntilChanged()
        //    .onEach { isActive ->
        //        if (isActive) start() else stop()
        //    }.launchIn(scope)
    }

    private fun callbackScreenResChanged(res : Point) {
        screenRes = res
        if (!isEncoderActive) {
            start()
        }
    }

    private fun suspend() {
        val params = Bundle()
        params.putInt(MediaCodec.PARAMETER_KEY_SUSPEND, 1)
        encoder.setParameters(params)
    }

    private fun resume() {
        val params = Bundle()
        params.putInt(MediaCodec.PARAMETER_KEY_SUSPEND, 0)
        params.putInt(MediaCodec.PARAMETER_KEY_REQUEST_SYNC_FRAME, 0)
        encoder.setParameters(params)
    }

    private fun start() {
        Log.d(TAG, "on encoder.start()")
        if (screenRes == null)
            return

        try {
            encoder = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_VIDEO_AVC)
            val format = MediaFormat.createVideoFormat(
                MediaFormat.MIMETYPE_VIDEO_AVC,
                screenRes!!.x, screenRes!!.y
            )
            format.setInteger(MediaFormat.KEY_BIT_RATE, 8 * 1000 * 1000)
            format.setInteger(MediaFormat.KEY_FRAME_RATE, 60)
            format.setInteger(
                MediaFormat.KEY_COLOR_FORMAT,
                MediaCodecInfo.CodecCapabilities.COLOR_FormatSurface
            )
            format.setInteger(MediaFormat.KEY_MAX_INPUT_SIZE, 0)
            format.setInteger(MediaFormat.KEY_REPEAT_PREVIOUS_FRAME_AFTER, 1000000)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                format.setInteger(MediaFormat.KEY_LATENCY, 0)
            }
            format.setInteger(MediaFormat.KEY_I_FRAME_INTERVAL, 5)
            // Set the encoder priority to realtime.
            format.setInteger(MediaFormat.KEY_PRIORITY, 0x00)
            encoder.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
            encoder.setInputSurface(surface)
            if (listener != null)
                encoder.setCallback(listener)
            encoder.start()
            Log.d(TAG, "Encoder configured")
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }

    private fun stop() {
        encoder.stop()
        encoder.release()
        Log.d(TAG, "Encoder stopped and released")
    }


    companion object {
        private val TAG = H264Converter::class.simpleName
    }
}