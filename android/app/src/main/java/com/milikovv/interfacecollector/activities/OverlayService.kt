package com.milikovv.interfacecollector.activities

import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.graphics.Point
import android.os.Build
import android.os.IBinder
import android.util.AttributeSet
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.TextView
import androidx.annotation.RequiresApi
import com.milikovv.interfacecollector.R

class OverlayService : Service() {
    private var mCurValue = 0

    private val overlay by lazy {
        View.inflate(applicationContext, R.layout.overlay_service, null)
//            .also {
//            it.findViewById<TextView>(R.id.text_hello).setOnClickListener {
//                stopSelf()
//            }
//        }
    }

    private val windowManager by lazy {
        applicationContext.getSystemService(Context.WINDOW_SERVICE) as WindowManager
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    @RequiresApi(Build.VERSION_CODES.O)
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_INCREMENT) {
            increaseValue()
            return START_STICKY
        }

        super.onStartCommand(intent, flags, startId)

        val layoutParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or
                    WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS or
                    WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
            PixelFormat.TRANSLUCENT
        ).also {
            it.gravity = Gravity.LEFT or Gravity.TOP
        }
        windowManager.addView(overlay, layoutParams)

        return START_STICKY
    }

    private fun increaseValue() {
        overlay.findViewById<TextView>(R.id.text_hello).text = mCurValue++.toString()
    }

    override fun onDestroy() {
        super.onDestroy()
        windowManager.removeView(overlay)
    }

    companion object {
        const val ACTION_INCREMENT = "INCREMENT_VALUE"
    }
}

class OverlayLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
        val screenSize = Point().also { windowManager.defaultDisplay.getRealSize(it) }

        super.onMeasure(
            MeasureSpec.makeMeasureSpec(screenSize.x, MeasureSpec.getMode(widthMeasureSpec)),
            MeasureSpec.makeMeasureSpec(screenSize.y, MeasureSpec.getMode(heightMeasureSpec))
        )
    }
}

class OverlayDrawingView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr)