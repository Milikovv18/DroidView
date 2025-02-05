package com.milikovv.interfacecollector.suppliers.media_projection

import android.R.mipmap.sym_def_app_icon
import android.app.Activity.RESULT_OK
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
import android.graphics.Point
import android.hardware.display.DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR
import android.hardware.display.VirtualDisplay
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Handler
import android.os.HandlerThread
import android.os.IBinder
import android.os.Looper
import android.os.Message
import android.os.Process
import android.util.DisplayMetrics
import android.util.Log
import android.view.Surface
import android.view.WindowManager
import android.widget.Toast
import com.milikovv.interfacecollector.ScreenResCallbackProvider
import dagger.android.AndroidInjection
import kotlinx.coroutines.runBlocking
import javax.inject.Inject


class MediaProjectionService : Service() {
    @Inject
    lateinit var surface: Surface
    @Inject
    lateinit var screenResCallback: ScreenResCallbackProvider

    private lateinit var mServiceHandler: ServiceHandler
    private lateinit var mMediaProjection: MediaProjection
    private lateinit var mVirtualDisplay: VirtualDisplay
    private lateinit var mScreenStateReceiver: BroadcastReceiver
    private var resultCode = 0
    private var data: Intent? = null

    private val TAG = "RECORDERSERVICE"
    private val EXTRA_RESULT_CODE = "resultcode"
    private val EXTRA_DATA = "data"
    private val ONGOING_NOTIFICATION_ID = 23
    private val CHANNEL_ID = "Collector channel"


    inner class MyBroadcastReceiver : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val data : Intent = this@MediaProjectionService.data!!
            when (intent.action) {
                Intent.ACTION_SCREEN_ON -> this@MediaProjectionService.startRecording(resultCode, data)
                Intent.ACTION_SCREEN_OFF -> this@MediaProjectionService.stopRecording()
                Intent.ACTION_CONFIGURATION_CHANGED -> {
                    this@MediaProjectionService.stopRecording()
                    this@MediaProjectionService.startRecording(resultCode, data)
                }
            }
        }
    }

    // Handler that receives messages from the thread
    private inner class ServiceHandler(looper: Looper) : Handler(looper) {
        override fun handleMessage(msg: Message) {
            if (this@MediaProjectionService.resultCode == RESULT_OK) {
                startRecording(resultCode, this@MediaProjectionService.data!!)
            }
        }
    }

    private inner class MPCallback : MediaProjection.Callback() {
        override fun onStop() {}
        override fun onCapturedContentResize(width: Int, height: Int) {}
        override fun onCapturedContentVisibilityChanged(isVisible: Boolean) {}
    }

    override fun onCreate() {
        AndroidInjection.inject(this)

        // run this service as foreground service to prevent it from getting killed
        // when the main app is being closed
        val notificationIntent = Intent(
            this,
            MediaProjectionService::class.java
        )
        val pendingIntent =
            PendingIntent.getActivity(this, 0, notificationIntent, PendingIntent.FLAG_IMMUTABLE)

        val channel = NotificationChannel(CHANNEL_ID, "Collector channel", NotificationManager.IMPORTANCE_HIGH)
        val notificationManager = getSystemService<NotificationManager>(NotificationManager::class.java)
        notificationManager.createNotificationChannel(channel)

        val notification: Notification =
            Notification.Builder(this, CHANNEL_ID)
                .setContentTitle("DataRecorder")
                .setContentText("Your screen is being recorded and saved to your phone.")
                .setSmallIcon(sym_def_app_icon)
                .setContentIntent(pendingIntent)
                .setTicker("Tickertext")
                .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(ONGOING_NOTIFICATION_ID, notification,
                FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION)
        } else {
            startForeground(ONGOING_NOTIFICATION_ID, notification)
        }

        // register receiver to check if the phone screen is on or off
        mScreenStateReceiver = MyBroadcastReceiver()
        val screenStateFilter = IntentFilter()
        screenStateFilter.addAction(Intent.ACTION_SCREEN_ON)
        screenStateFilter.addAction(Intent.ACTION_SCREEN_OFF)
        screenStateFilter.addAction(Intent.ACTION_CONFIGURATION_CHANGED)
        registerReceiver(mScreenStateReceiver, screenStateFilter)

        val thread = HandlerThread(
            "ServiceStartArguments",
            Process.THREAD_PRIORITY_BACKGROUND
        )
        thread.start()

        val mServiceLooper = thread.looper
        mServiceHandler = ServiceHandler(mServiceLooper)

        mThis = this
    }

    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        Toast.makeText(this, "Starting recording service", Toast.LENGTH_SHORT).show()

        resultCode = intent.getIntExtra(EXTRA_RESULT_CODE, 0)
        data = intent.getParcelableExtra(EXTRA_DATA)

        check(!(resultCode == 0 || data == null)) { "Result code or data missing." }

        val msg: Message = mServiceHandler.obtainMessage()
        msg.arg1 = startId
        mServiceHandler.sendMessage(msg)

        return START_REDELIVER_INTENT
    }

    private fun startRecording(resultCode: Int, data: Intent) {
        val mProjectionManager =
            applicationContext.getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager

        val metrics = DisplayMetrics()
        val wm = applicationContext.getSystemService(WINDOW_SERVICE) as WindowManager
        wm.defaultDisplay.getRealMetrics(metrics)

        val mScreenDensity = metrics.densityDpi
        val displayWidth = metrics.widthPixels
        val displayHeight = metrics.heightPixels

        runBlocking {
            screenResCallback.flow.emit(Point(metrics.widthPixels, metrics.heightPixels))
        }

        mMediaProjection = mProjectionManager.getMediaProjection(resultCode, data)
        mMediaProjection.registerCallback(MPCallback(), null)
        mVirtualDisplay = mMediaProjection.createVirtualDisplay(
            "MainActivity",
            displayWidth, displayHeight, mScreenDensity, VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            surface, null, null
        )
        
        Log.v(TAG, "Started recording")
    }

    private fun stopRecording() {
        mMediaProjection.stop()
        mVirtualDisplay.release()
    }

    override fun onBind(intent: Intent?): IBinder? {
        // We don't provide binding, so return null
        return null
    }

    override fun onDestroy() {
        //stopRecording()
        //unregisterReceiver(mScreenStateReceiver)
        //stopSelf()
        //Toast.makeText(this, "Recorder service stopped", Toast.LENGTH_SHORT).show()
    }


    companion object {
        private val EXTRA_RESULT_CODE = "resultcode"
        private val EXTRA_DATA = "data"
        private var mThis : MediaProjectionService? = null

        fun newIntent(context: Context?, resultCode: Int, data: Intent?): Intent {
            val intent = Intent(context, MediaProjectionService::class.java)
            intent.putExtra(EXTRA_RESULT_CODE, resultCode)
            intent.putExtra(EXTRA_DATA, data)
            return intent
        }
    }
}