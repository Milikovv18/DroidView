package com.milikovv.interfacecollector.suppliers.accessibility

import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import com.milikovv.interfacecollector.suppliers.Supplier
import com.milikovv.interfacecollector.suppliers.accessibility.serializers.SerializableNode
import kotlinx.coroutines.flow.MutableSharedFlow
import java.util.Stack


abstract class AccessibilityListener : Supplier<String> {
    var rootGetter : (() -> AccessibilityNodeInfo)? = null

    private var hotFlow = MutableSharedFlow<String>()

    fun onAccessibilityEvent(event: AccessibilityEvent?) {
        val root = event?.source ?: return
        //Log.d(TAG, "Sending to hot stream")

        //hotFlow.tryEmit(processHierarchy(root) ?: return)
    }

    override fun getHotStream(): MutableSharedFlow<String> = hotFlow

    protected fun parseHierarchy(root: AccessibilityNodeInfo) : SerializableNode {
        val unprocessed = Stack<AccessibilityNodeInfo>()
        val processed = Stack<SerializableNode>()
        val result = serializify(root)
        unprocessed.push(root)
        processed.push(result)

        while (!unprocessed.empty()) {
            val node = unprocessed.pop()
            val parent = processed.pop()
            for (i in 0..< node.childCount) {
                val child = node.getChild(i) ?: continue
                unprocessed.push(child)
                val serialized = serializify(child)
                parent.children.add(serialized)
                processed.push(serialized)
            }
        }
        return result
    }


    abstract override fun getOnce(callback : ((String?) -> Unit))

    protected abstract fun processHierarchy(root: AccessibilityNodeInfo) : String

    protected abstract fun serializify(node : AccessibilityNodeInfo) : SerializableNode


    companion object {
        private val TAG = AccessibilityListener::class.simpleName
    }
}