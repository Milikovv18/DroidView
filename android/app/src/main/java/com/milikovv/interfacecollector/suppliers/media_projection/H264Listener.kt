package com.milikovv.interfacecollector.suppliers.media_projection

import android.media.MediaCodec
import android.media.MediaFormat
import android.util.Log
import com.milikovv.interfacecollector.suppliers.Supplier
import com.octiplex.android.rtmp.H264VideoFrame
import kotlinx.coroutines.flow.MutableSharedFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class H264Listener @Inject constructor(
    configurator: H264Converter
) : Supplier<H264VideoFrame>, MediaCodec.Callback() {
    private val hotFlow = MutableSharedFlow<H264VideoFrame>(extraBufferCapacity = 1000)
    private var isInitialHeaderSent = false

    init {
        configurator.setListener(this)
    }

    override fun onInputBufferAvailable(codec: MediaCodec, index: Int) {
        Log.d(TAG, "onInputBufferAvailable")
    }

    override fun onOutputBufferAvailable(codec: MediaCodec, index: Int, info: MediaCodec.BufferInfo) {
        Log.d(TAG, "onOutputBufferAvailable")

        try {
            val outputBuffer = codec.getOutputBuffer(index) ?: return
            val array = ByteArray(outputBuffer.limit() - outputBuffer.position())
            outputBuffer.get(array)

            // Start sending video only when RTMP is fully configured
            if (isInitialHeaderSent)
                hotFlow.tryEmit(makeFrame(array, info))

            codec.releaseOutputBuffer(index, false)
        } catch (e: IllegalStateException) {
            return
        }
    }

    override fun onError(codec: MediaCodec, e: MediaCodec.CodecException) {
        Log.d(TAG, "onError")
    }

    override fun onOutputFormatChanged(codec: MediaCodec, format: MediaFormat) {
        Log.d(
            TAG, "Updated output format! New height:"
                    + format.getInteger(MediaFormat.KEY_HEIGHT) + " new width: " +
                    format.getInteger(MediaFormat.KEY_WIDTH)
        )

        val sps = format.getByteBuffer("csd-0")!!
        var header = ByteArray(sps.remaining())
        sps.get(header)

        val pps = format.getByteBuffer("csd-1")!!
        val array = ByteArray(pps.remaining())
        pps.get(array)
        header += array

        val headerBuf = MediaCodec.BufferInfo()
        headerBuf.set(0, 0, System.currentTimeMillis(), MediaCodec.BUFFER_FLAG_CODEC_CONFIG)

        hotFlow.tryEmit(makeFrame(header, headerBuf))
        isInitialHeaderSent = true
    }

    private fun makeFrame(buffer: ByteArray, info: MediaCodec.BufferInfo) : H264VideoFrame {
        return object: H264VideoFrame {
            override fun isHeader(): Boolean {
                return (info.flags and MediaCodec.BUFFER_FLAG_CODEC_CONFIG) != 0
            }

            override fun getTimestamp(): Long {
                return info.presentationTimeUs / 1000
            }

            override fun getData(): ByteArray {
                return buffer
            }

            override fun isKeyframe(): Boolean {
                return !isHeader && (info.flags and MediaCodec.BUFFER_FLAG_KEY_FRAME) != 0
            }
        }
    }


    override fun getHotStream(): MutableSharedFlow<H264VideoFrame> = hotFlow

    override fun getOnce(callback : ((H264VideoFrame?) -> Unit)) {
        TODO("Not yet implemented")
    }


    companion object {
        val TAG = H264Listener::class.simpleName
    }
}