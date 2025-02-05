package com.milikovv.interfacecollector.suppliers.accessibility.serializers

import android.graphics.Rect
import android.util.Log
import android.view.accessibility.AccessibilityNodeInfo
import com.milikovv.interfacecollector.suppliers.accessibility.AccessibilityListener
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.ClassDiscriminatorMode
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.coroutines.CoroutineContext


@Singleton
class MinimalAccessibilityListener @Inject constructor() : AccessibilityListener() {
    private val jsonMapper = Json {
        encodeDefaults = false
        classDiscriminatorMode = ClassDiscriminatorMode.NONE
    }

    private val coroutineContext: CoroutineContext = Job()
    private val scope: CoroutineScope = CoroutineScope(coroutineContext)
    private val callbackFlow = MutableSharedFlow<((String?) -> Unit)>(extraBufferCapacity = 1)

    init {
        scope.launch {
            callbackFlow.collectLatest { callback ->
                callback(rootGetter?.invoke()?.let { processHierarchy(it) })
            }
        }
    }

    override fun getOnce(callback : ((String?) -> Unit)) {
        if (!callbackFlow.tryEmit(callback))
            callback(jsonMapper.encodeToString(VisualizableNode(540, 1200, 1080, 2400)))
    }

    override fun processHierarchy(root: AccessibilityNodeInfo) : String {
        return jsonMapper.encodeToString(super.parseHierarchy(root))
    }

    override fun serializify(node : AccessibilityNodeInfo): VisualizableNode {
        val bounds = Rect()
        node.getBoundsInScreen(bounds)
        return VisualizableNode(
            x = bounds.centerX(),
            y = bounds.centerY(),
            w = bounds.width(),
            h = bounds.height()
        )
    }


    companion object {
        private val TAG = MinimalAccessibilityListener::class.java.simpleName
    }
}