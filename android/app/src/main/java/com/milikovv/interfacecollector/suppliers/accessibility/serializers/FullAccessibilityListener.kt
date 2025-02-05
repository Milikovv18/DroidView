package com.milikovv.interfacecollector.suppliers.accessibility.serializers

import android.graphics.Rect
import android.os.Build
import android.util.Log
import android.view.accessibility.AccessibilityNodeInfo
import com.milikovv.interfacecollector.suppliers.accessibility.AccessibilityListener
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.ClassDiscriminatorMode
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton


@Singleton
class FullAccessibilityListener @Inject constructor() : AccessibilityListener() {
    private val jsonMapper = Json {
        encodeDefaults = false;
        classDiscriminatorMode = ClassDiscriminatorMode.NONE
    }

    override fun getOnce(callback : ((String?) -> Unit)) {
        Log.d("Full", "Inside getOnce with " + (rootGetter != null))
        callback(rootGetter?.invoke()?.let { processHierarchy(it) })
    }

    override fun processHierarchy(root: AccessibilityNodeInfo) : String {
        return jsonMapper.encodeToString(super.parseHierarchy(root))
    }

    override fun serializify(node : AccessibilityNodeInfo): DescriptiveNode {
        val bounds = Rect()
        node.getBoundsInScreen(bounds)
        return DescriptiveNode(
            booleans = maskFromBooleans(node),
            // Text
            className  = node.className?.toString(),
            containerTitle  = if (Build.VERSION.SDK_INT >= 34) node.containerTitle?.toString() else null,
            contentDescription  = node.contentDescription?.toString(),
            errorText  = node.error?.toString(),
            hintText  = if (Build.VERSION.SDK_INT >= 26) node.hintText?.toString() else null,
            tooltipText  = if (Build.VERSION.SDK_INT >= 28) node.tooltipText?.toString() else null,
            packageName  = node.packageName.toString(),
            paneTitle  = if (Build.VERSION.SDK_INT >= 28) node.paneTitle?.toString() else null,
            stateDescription  = if (Build.VERSION.SDK_INT >= 30) node.stateDescription?.toString() else null,
            text  = node.text?.toString(),
            uniqueId  = if (Build.VERSION.SDK_INT >= 33) node.uniqueId else null,
            viewIdResourceName  = node.viewIdResourceName?.toString(),
            // Numbers
            drawingOrder  = if (Build.VERSION.SDK_INT >= 24) node.drawingOrder else 0,
            inputType  = node.inputType,
            // Misc
            x = bounds.centerX(),
            y = bounds.centerY(),
            w = bounds.width(),
            h = bounds.height(),
            actionList = collectActions(node.actionList)
        )
    }

    private fun Boolean.toInt() = if (this) 1 else 0
    private fun maskFromBooleans(node : AccessibilityNodeInfo) : Int {
        var result = 0
        result = result or (node.canOpenPopup().toInt() shl 0)
        result = result or ((if (Build.VERSION.SDK_INT >= 34) node.isAccessibilityDataSensitive else false).toInt() shl 1)
        result = result or (node.isAccessibilityFocused.toInt() shl 2)
        result = result or (node.isCheckable.toInt() shl 4)
        result = result or (node.isChecked.toInt() shl 8)
        result = result or (node.isClickable.toInt() shl 16)
        result = result or (node.isContentInvalid.toInt() shl 32)
        result = result or ((if (Build.VERSION.SDK_INT >= 23) node.isContextClickable else false).toInt() shl 64)
        result = result or (node.isDismissable.toInt() shl 128)
        result = result or (node.isEditable.toInt() shl 256)
        result = result or (node.isEnabled.toInt() shl 512)
        result = result or (node.isFocusable.toInt() shl 1024)
        result = result or (node.isFocused.toInt() shl 2048)
        result = result or ((if (Build.VERSION.SDK_INT >= 28) node.isHeading else false).toInt() shl 4096)
        result = result or ((if (Build.VERSION.SDK_INT >= 24) node.isImportantForAccessibility else false).toInt() shl 8192)
        result = result or (node.isLongClickable.toInt() shl 16384)
        result = result or (node.isMultiLine.toInt() shl 32768)
        result = result or (node.isPassword.toInt() shl 65536)
        result = result or ((if (Build.VERSION.SDK_INT >= 28) node.isScreenReaderFocusable else false).toInt() shl 131072)
        result = result or (node.isScrollable.toInt() shl 262144)
        result = result or (node.isSelected.toInt() shl 524288)
        result = result or ((if (Build.VERSION.SDK_INT >= 26) node.isShowingHintText else false).toInt() shl 1048578)
        result = result or ((if (Build.VERSION.SDK_INT >= 29) node.isTextEntryKey else false).toInt() shl 2097156)
        result = result or ((if (Build.VERSION.SDK_INT >= 33) node.isTextSelectable else false).toInt() shl 4194312)
        result = result or (node.isVisibleToUser.toInt() shl 8388624)
        return result
    }

    private fun collectActions(actions : List<AccessibilityNodeInfo.AccessibilityAction>) : List<Long> {
        var simpleActions = 0L
        val customActions = ArrayList<Long>()
        for (action in actions) {
            val id : Long = action.id.toLong()
            if ((id and 0xFF000000L) == 0L)
                simpleActions = simpleActions or id
            else
                customActions.add(id)
        }
        customActions.add(0, simpleActions)
        return customActions
    }
}