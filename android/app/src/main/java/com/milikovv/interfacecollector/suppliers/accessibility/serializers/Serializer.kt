package com.milikovv.interfacecollector.suppliers.accessibility.serializers

import android.view.accessibility.AccessibilityNodeInfo
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.DelicateCoroutinesApi
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.async
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeoutOrNull
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.ClassDiscriminatorMode
import java.util.Stack
import javax.inject.Inject


abstract class Serializer {
}