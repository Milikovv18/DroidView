package com.milikovv.interfacecollector.suppliers.accessibility

import android.accessibilityservice.AccessibilityService
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import dagger.android.AndroidInjection
import java.util.Date
import javax.inject.Inject

class AccessibilityServiceService : AccessibilityService() {
    @Inject
    lateinit var children: Set<@JvmSuppressWildcards AccessibilityListener>

    private var startButtonClicked = false
    private var lastTime = 0L

    override fun onServiceConnected() {
        AndroidInjection.inject(this)
        super.onServiceConnected()

        Log.d(TAG, "Initializing " + children.size + " children")
        for (child in children)
            child.rootGetter = this::getRootInActiveWindow

        Log.d(TAG, "Hierarchy retriever connected. Ready to collect data")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        val root = event?.source ?: return

        if (!startButtonClicked)
            clickStartButton(root)

        for (child in children)
            child.onAccessibilityEvent(event)
    }

    private fun clickStartButton(root : AccessibilityNodeInfo) {
        val list = root.findAccessibilityNodeInfosByViewId(START_RECORD_BTN_ID) ?: return
        if (list.isEmpty())
            return
        list[0].performAction(AccessibilityNodeInfo.ACTION_CLICK)
        startButtonClicked = true
    }

    private fun appendToDataset(root: AccessibilityNodeInfo) {
        val currentTime = Date().time
        if (currentTime > lastTime + TIME_STEP_MS) {
            lastTime = currentTime

            // Increasing value on screen
            //val i = Intent(this, OverlayService::class.java)
            //i.setAction(OverlayService.ACTION_INCREMENT)
            //startService(i)

            //val hierarchy = serializationEngine.processHierarchy(root) ?: return

            // Saving hierarchy to file
            //val fileName = File("$path/$currentTime.json")
            //Log.d(TAG, "Saving to file $fileName...")
            //fileName.createNewFile()
            //fileName.writeText(hierarchy)
        }
    }

    override fun onInterrupt() {
        TODO("Not yet implemented")
    }


    companion object {
        private val TAG = AccessibilityServiceService::class.simpleName

        private const val START_RECORD_BTN_ID = "android:id/button1"
        private const val TIME_STEP_MS = 500
    }
}
